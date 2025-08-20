#ifndef __dbg_h__
#define __dbg_h__

#include <stdio.h>
#include <errno.h>
#include <string.h>

// See the Standard Predefined Macros 
// https://gcc.gnu.org/onlinedocs/cpp/Standard-Predefined-Macros.html

// forward declarations for compatibility with older versions of gcc
// see https://github.com/numpy/numpy/issues/16970
// also see https://github.com/lpsinger/ligo.skymap/commit/b1bc1ab05b613012d0cc4fcaf4e76bcd9e038792
#define PyLIMITED_API 0x03060000
struct _typeobject {};

#ifdef NDEBUG
#define debug(M, ...)
#else
#define debug(M, ...) fprintf(stderr,\
    "DEBUG %s:%d -> %s: " M "\n",\
    __FILE__, __LINE__, __FUNCTION__ , ##__VA_ARGS__)
#endif

#define clean_errno() (errno == 0 ? "None" : strerror(errno))

#define log_err(M, ...) fprintf(stderr,\
    "[ERROR] (%s:%d -> %s: errno: %s) " M "\n",\
    __FILE__, __LINE__, __FUNCTION__,\
    clean_errno(), ##__VA_ARGS__)

#define log_warn(M, ...) fprintf(stderr,\
    "[WARN] (%s:%d -> %s: errno: %s) " M "\n",\
    __FILE__, __LINE__, __FUNCTION__,\
    clean_errno(), ##__VA_ARGS__)

#define log_info(M, ...) fprintf(stderr, "[INFO] (%s:%d -> %s) " M "\n",\
    __FILE__, __LINE__, __FUNCTION__,\
    ##__VA_ARGS__)

#define check(A, M, ...) if(!(A)) {\
    log_err(M, ##__VA_ARGS__); errno=0; goto error; }

#define sentinel(M, ...) {log_err(M, ##__VA_ARGS__);\
    errno=0; goto error; }

#define check_mem(A) check((A), "Out of memory.")

#define check_debug(A, M, ...) if(!(A)) { debug(M, ##__VA_ARGS__);\
    errno=0; goto error; }

#endif
