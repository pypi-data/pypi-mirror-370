/*
MIT License

Copyright (c) 2017 John Bryan Moore
Copyright (c) 2024 Jakub Frgal

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>
#include <time.h>
#include "vl53lx_api.h"
#include "vl53lx_platform.h"

static VL53LX_MultiRangingData_t MultiRangingData;
static VL53LX_MultiRangingData_t *pMultiRangingData = &MultiRangingData;

/******************************************************************************
 * @brief   Initialises the device.
 *  @param  i2c_address - I2C Address to set for this device
 * @retval  The Dev Object to pass to other library functions.
 *****************************************************************************/
VL53LX_DEV *initialise(uint8_t i2c_address, uint8_t perform_reset)
{
    VL53LX_Error Status = VL53LX_ERROR_NONE;
    uint32_t refSpadCount;
    uint8_t isApertureSpads;
    uint8_t VhvSettings;
    uint8_t PhaseCal;
    VL53LX_Version_t Version;
    VL53LX_Version_t *pVersion = &Version;
    VL53LX_DeviceInfo_t DeviceInfo;
    int32_t status_int;
    uint8_t ModelId, ModuleType, MaskRev;

    VL53LX_Dev_t *dev = (VL53LX_Dev_t *)malloc(sizeof(VL53LX_Dev_t));
    memset(dev, 0, sizeof(VL53LX_Dev_t));

    dev->I2cDevAddr = i2c_address;

    Status = VL53LX_RdByte(dev, 0x010F, &ModelId);
    Status = VL53LX_RdByte(dev, 0x0110, &ModuleType);
    Status = VL53LX_RdByte(dev, 0x0111, &MaskRev);
    
    Status = VL53LX_WaitDeviceBooted(dev);
    Status = VL53LX_DataInit(dev);
    
    VL53LX_PerformRefSpadManagement(dev);
    VL53LX_SetXTalkCompensationEnable(dev, 0); // Disable crosstalk compensation (bare sensor)

    return dev;
}

VL53LX_Error setDeviceAddress(VL53LX_Dev_t *dev, int i2c_address)
{
    VL53LX_Error Status = VL53LX_SetDeviceAddress(dev, i2c_address << 1);
    if(Status == VL53LX_ERROR_NONE){
        dev->I2cDevAddr = i2c_address;
    }
    return Status;
}

/******************************************************************************
 * @brief   Set Distance Mode
 * @param   mode - ranging mode
 *              1 - Short-range mode
 *              2 - Medium-range mode
 *              3 - Long-range mode
 * @retval  Error code, 0 for success.
 *****************************************************************************/
VL53LX_Error setDistanceMode(VL53LX_Dev_t *dev, int mode)
{
    VL53LX_Error Status = VL53LX_ERROR_NONE;
    Status = VL53LX_SetDistanceMode(dev, mode);
    return Status;
}


/******************************************************************************
 * @brief   Start Ranging
 * @retval  Error code, 0 for success.
 *****************************************************************************/
VL53LX_Error startRanging(VL53LX_Dev_t *dev)
{
    VL53LX_Error Status = VL53LX_ERROR_NONE;
    Status = VL53LX_StartMeasurement(dev);
    return Status;
}

/******************************************************************************
 * @brief   Set the measurement timing budget in microseconds
 * @return  Error code, 0 for success.
 *****************************************************************************/
VL53LX_Error setMeasurementTimingBudgetMicroSeconds(VL53LX_Dev_t *dev, int timing_budget) {
    return VL53LX_SetMeasurementTimingBudgetMicroSeconds(dev, timing_budget);
}

/******************************************************************************
 * @brief   Get current distance in mm
 * @return  Current distance in mm or -1 on error
 *****************************************************************************/
int32_t getDistance(VL53LX_Dev_t *dev)
{
    VL53LX_Error Status = VL53LX_ERROR_NONE;
    int32_t current_distance = -1;
    Status = VL53LX_GetMultiRangingData(dev, pMultiRangingData);
    current_distance = pMultiRangingData->RangeData[0].RangeMilliMeter;
    VL53LX_ClearInterruptAndStartMeasurement(dev);
    return current_distance;
}

/******************************************************************************
 * @brief   Check if new data is ready
 * @return  True if new data is ready, False otherwise
 *****************************************************************************/
uint8_t isRangingReady(VL53LX_Dev_t *dev)
{
    VL53LX_Error Status = VL53LX_ERROR_NONE;
    uint8_t MeasurementDataReady;
    Status = VL53LX_GetMeasurementDataReady(dev, &MeasurementDataReady);
    return MeasurementDataReady;
}

/******************************************************************************
 * @brief   Wait for measurment data and get them
 * @return  Current distance in mm or -1 on error
 *****************************************************************************/
int32_t waitForData(VL53LX_Dev_t *dev)
{
    VL53LX_Error Status = VL53LX_ERROR_NONE;
    int32_t current_distance = -1;
    Status = VL53LX_WaitMeasurementDataReady(dev);
    Status = VL53LX_GetMultiRangingData(dev, pMultiRangingData);
    current_distance = pMultiRangingData->RangeData[0].RangeMilliMeter;
    VL53LX_ClearInterruptAndStartMeasurement(dev);
    return current_distance;
}

/******************************************************************************
 * @brief   Stop Ranging
 *****************************************************************************/
VL53LX_Error stopRanging(VL53LX_Dev_t *dev)
{
    VL53LX_StopMeasurement(dev);
}
