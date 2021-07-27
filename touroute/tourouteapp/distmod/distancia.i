%module distancia

%{
#define SWIG_FILE_WITH_INIT
#include "distancia.h"
%}

float distancef(float lon1, float lat1, float lon2, float lat2);
