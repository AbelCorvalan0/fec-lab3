#include <stdio.h>
#include <string.h>
#include <Python.h>
#include <svdpi.h>

// Global pointers to keep the Python object alive during simulation
PyObject *pInstance = NULL;
PyObject *pMethod = NULL;

void set_pythonpath() {
    // Get <path>/<filename> string with ending '\0'
    char *dir_path = (char *) malloc(strlen(__FILE__) + 1);
    strcpy(dir_path, __FILE__);

    // Remove filename, ending string with '\0'
    char *last_slash = strrchr(dir_path, '/');
    if (last_slash != NULL) {
        *last_slash = '\0'; 
    }

    setenv("PYTHONPATH", dir_path, 1);
    // setenv("PYTHONPATH", "/home/clifferto/Documents/carrerpath/projects/fec_work/arch/bch_15_5/encoder/model", 1);
    char *env_val = getenv("PYTHONPATH");
    if (env_val != NULL) {
        printf("Variable PYTHONPATH: %s\n", env_val);
    }
    free(dir_path);
}

// Called during scoreboard build_phase to initialize Python
void model_create() {
    // Set PYTHONPATH with THIS file location
    set_pythonpath();
    // It will automatically read your terminal's PYTHONPATH variable here.
    Py_Initialize();
    // PyRun_SimpleString("import sys; sys.path.append('/home/clifferto/Documents/carrerpath/projects/fec_work/arch/bch_15_5/encoder/model'); print(sys.path)");
    
    // Import the module and get the class
    PyObject *pName = PyUnicode_FromString("classes.bch_encoder");
    PyObject *pModule = PyImport_Import(pName);
    if (pModule != NULL) {
        PyObject *pClass = PyObject_GetAttrString(pModule, "BchEncoder");
        if (pClass && PyCallable_Check(pClass)) {
            // Instantiate the class, and cache the get_output method pointer
            pInstance = PyObject_CallObject(pClass, NULL);
            pMethod = PyObject_GetAttrString(pInstance, "get_output");
        }
        Py_DECREF(pModule);
    }
}

// The function exported to SystemVerilog
int model_get_output(int word) {
    int result = 0;
    if (pMethod && PyCallable_Check(pMethod)) {
        // Pack arguments into a Python tuple
        PyObject *pArgs = PyTuple_Pack(1, PyLong_FromLong(word));
        // Call: model.get_output(word)
        PyObject *pValue = PyObject_CallObject(pMethod, pArgs);
        
        if (pValue != NULL) {
            result = (int)PyLong_AsLong(pValue);
            
            printf("From C: model_get_output(%05b) = %015b\n", word, result);
            
            Py_DECREF(pValue);
        }
        Py_DECREF(pArgs);
    }
    return result;
}

// Clean up memory at the end of simulation
void model_cleanup() {
    if(pMethod) Py_DECREF(pMethod);
    if(pInstance) Py_DECREF(pInstance);
    Py_Finalize();
}

// Linker Error Root Cause:
// 
//     Vivado 2025.2: older version of the GNU Linker (binutils-2.37/bin/ld)
//     Modern Linux distributions: added a newer optimization called .relr.dyn packing inside /lib64/libm.so.6.
// 
//     Vivado older ld --> unknown type [0x13] section '.relr.dyn' --> fails to link your libdpi.so.
// 
// The Fix: Bypass Vivado's Linker
// 
//     cd /home/clifferto/tools/2025.2/Vivado/tps/lnx64/binutils-2.37/bin/
//     # 2. Rename the incompatible linker so Vivado can't find it
//     mv ld ld.backup
//     # 3. Create a symbolic link pointing to your OS system linker instead
//     ln -s /usr/bin/ld ld
// 
// Install Python.h for DIP-C
// 
//      sudo dnf install python3-devel
//      Config vivado:
//          tools > settings > Simulation > Compilation > xsim.compile.xsc.more_options: --gcc_compile_options "-I/usr/include/python3.14"
// 
// Config PYTHONPATH in vivado tcl console
//
//      launch vivado > open project > tcl console
//      souce <path set_pythonpath.tcl>
