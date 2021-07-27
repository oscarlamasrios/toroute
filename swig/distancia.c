#include <stdio.h>
#include <stdlib.h>
#include <math.h>

float distancef(float lon1, float lat1, float lon2, float lat2)
{
	float x;
	x = sqrt((lon1-lon2)*(lon1-lon2)+(lat1-lat2)*(lat1-lat2));
	return x;
}

