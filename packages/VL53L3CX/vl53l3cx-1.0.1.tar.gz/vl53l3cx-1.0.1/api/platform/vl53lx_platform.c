#include "vl53lx_platform.h"
#include "vl53lx_api.h"

#include <pthread.h>
#include <string.h>
#include <time.h>

#include <unistd.h>


// calls read_i2c_block_data(address, reg, length)
static int (*i2c_read_func)(uint8_t address, uint16_t reg,
					uint8_t *list, uint8_t length) = NULL;

// calls write_i2c_block_data(address, reg, list)
static int (*i2c_write_func)(uint8_t address, uint16_t reg,
					uint8_t *list, uint8_t length) = NULL;

static pthread_mutex_t i2c_mutex = PTHREAD_MUTEX_INITIALIZER;

void VL53LX_set_i2c(void *read_func, void *write_func)
{
	i2c_read_func = read_func;
	i2c_write_func = write_func;
}

static int i2c_write(VL53LX_DEV Dev, uint16_t cmd,
                    uint8_t *data, uint8_t len)
{
    int result = VL53LX_ERROR_NONE;

    if (i2c_write_func != NULL)
    {
		pthread_mutex_lock(&i2c_mutex);

		if (i2c_write_func(Dev->I2cDevAddr, cmd, data, len) < 0)
		{
			result =  VL53LX_ERROR_CONTROL_INTERFACE;
		}
            
		pthread_mutex_unlock(&i2c_mutex);
        }
    else
    {
        printf("i2c bus write not set.\n");
        result = VL53LX_ERROR_CONTROL_INTERFACE;
    }
    
    return result;
}

static int i2c_read(VL53LX_DEV Dev, uint16_t cmd,
                    uint8_t * data, uint8_t len)
{
    int result = VL53LX_ERROR_NONE;

    if (i2c_read_func != NULL)
    {
		pthread_mutex_lock(&i2c_mutex);

		if (i2c_read_func(Dev->I2cDevAddr, cmd, data, len) < 0)
		{
			result =  VL53LX_ERROR_CONTROL_INTERFACE;
		}

		pthread_mutex_unlock(&i2c_mutex);
    }
    else
    {
        printf("i2c bus read not set.\n");
        result =  VL53LX_ERROR_CONTROL_INTERFACE;
    }
    
    return result;
}

VL53LX_Error VL53LX_WriteMulti(VL53LX_DEV pdev, uint16_t index, uint8_t *pdata, uint32_t count) {
	return i2c_write(pdev, index, pdata, count);

	//VL53LX_Error Status = VL53LX_ERROR_NONE;
	//return Status;
}

// the ranging_sensor_comms.dll will take care of the page selection
VL53LX_Error VL53LX_ReadMulti(VL53LX_DEV pdev, uint16_t index, uint8_t *pdata, uint32_t count) {
	return i2c_read(pdev, index, pdata, count);

	//VL53LX_Error Status = VL53LX_ERROR_NONE;
	//return Status;
}

VL53LX_Error VL53LX_WrByte(VL53LX_DEV pdev, uint16_t index, uint8_t data) {
	return i2c_write(pdev, index, &data, 1);

	//VL53LX_Error Status = VL53LX_ERROR_NONE;
	//return Status;
}

VL53LX_Error VL53LX_WrWord(VL53LX_DEV pdev, uint16_t index, uint16_t data) {
	uint8_t buf[4];
	buf[1] = data>>0&0xFF;
	buf[0] = data>>8&0xFF;
	return i2c_write(pdev, index, buf, 2);

	//VL53LX_Error Status = VL53LX_ERROR_NONE;
	//return Status;
}

VL53LX_Error VL53LX_WrDWord(VL53LX_DEV pdev, uint16_t index, uint32_t data) {
	uint8_t buf[4];
	buf[3] = data>>0&0xFF;
	buf[2] = data>>8&0xFF;
	buf[1] = data>>16&0xFF;
	buf[0] = data>>24&0xFF;
	return i2c_write(pdev, index, buf, 4);

	//VL53LX_Error Status = VL53LX_ERROR_NONE;
	//return Status;
}

VL53LX_Error VL53LX_UpdateByte(VL53LX_DEV pdev, uint16_t index, uint8_t AndData, uint8_t OrData) {
	int32_t status_int;
	uint8_t data;

	status_int = i2c_read(pdev, index, &data, 1);

	if (status_int != 0)
	{
		return  status_int;
	}

	data = (data & AndData) | OrData;
	return i2c_write(pdev, index, &data, 1);

	//VL53LX_Error Status = VL53LX_ERROR_NONE;
	//return Status;
}

VL53LX_Error VL53LX_RdByte(VL53LX_DEV pdev, uint16_t index, uint8_t *data) {
	uint8_t tmp = 0;
	int ret = i2c_read(pdev, index, &tmp, 1);
	*data = tmp;
	return ret;

	//VL53LX_Error Status = VL53LX_ERROR_NONE;
	//return Status;
}

VL53LX_Error VL53LX_RdWord(VL53LX_DEV pdev, uint16_t index, uint16_t *data) {
	uint8_t buf[2];
	int ret = i2c_read(pdev, index, buf, 2);
	uint16_t tmp = 0;
	tmp |= buf[1]<<0;
	tmp |= buf[0]<<8;
	*data = tmp;
	return ret;

	//VL53LX_Error Status = VL53LX_ERROR_NONE;
	//return Status;
}

VL53LX_Error VL53LX_RdDWord(VL53LX_DEV pdev, uint16_t index, uint32_t *data) {
	uint8_t buf[4];
	int ret = i2c_read(pdev, index, buf, 4);
	uint32_t tmp = 0;
	tmp |= buf[3]<<0;
	tmp |= buf[2]<<8;
	tmp |= buf[1]<<16;
	tmp |= buf[0]<<24;
	*data = tmp;
	return ret;

	//VL53LX_Error Status = VL53LX_ERROR_NONE;
	//return Status;
}

VL53LX_Error VL53LX_GetTickCount(
	uint32_t *ptick_count_ms)
{
	VL53LX_Error status  = VL53LX_ERROR_NONE;
	return status;
}

//#define trace_print(level, ...) \
//	_LOG_TRACE_PRINT(VL53LX_TRACE_MODULE_PLATFORM, \
//	level, VL53LX_TRACE_FUNCTION_NONE, ##__VA_ARGS__)

//#define trace_i2c(...) \
//	_LOG_TRACE_PRINT(VL53LX_TRACE_MODULE_NONE, \
//	VL53LX_TRACE_LEVEL_NONE, VL53LX_TRACE_FUNCTION_I2C, ##__VA_ARGS__)

VL53LX_Error VL53LX_GetTimerFrequency(int32_t *ptimer_freq_hz)
{
	VL53LX_Error status  = VL53LX_ERROR_NONE;
	return status;
}

VL53LX_Error VL53LX_WaitMs(VL53LX_DEV pdev, int32_t wait_ms){
	sleep(wait_ms / 1000);
    return VL53LX_ERROR_NONE;
}

VL53LX_Error VL53LX_WaitUs(VL53LX_DEV pdev, int32_t wait_us){
	sleep(wait_us / 1000000);
    return VL53LX_ERROR_NONE;
}

VL53LX_Error VL53LX_WaitValueMaskEx(
	VL53LX_DEV pdev,
	uint32_t   timeout_ms,
	uint16_t   index,
	uint8_t	   value,
	uint8_t	   mask,
	uint32_t   poll_delay_ms)
{
	uint8_t  register_value = 0;

	VL53LX_Error status  = VL53LX_ERROR_NONE;

	int32_t attempts = timeout_ms / poll_delay_ms;

	for(int32_t x = 0; x < attempts; x++){
		status = VL53LX_RdByte(
					pdev,
					index,
					&register_value);
		if (status == VL53LX_ERROR_NONE && (register_value & mask) == value) {
			return VL53LX_ERROR_NONE;
		}
		sleep(poll_delay_ms / 1000);
	}

	return VL53LX_ERROR_TIME_OUT;
}

VL53LX_Error VL53LX_GpioXshutdown(uint8_t value)
{
  return VL53LX_ERROR_NONE;
}

VL53LX_Error VL53LX_GpioCommsSelect(uint8_t value)
{
  return VL53LX_ERROR_NONE;
}

VL53LX_Error VL53LX_GpioPowerEnable(uint8_t value)
{
  return VL53LX_ERROR_NONE;
}

VL53LX_Error VL53LX_CommsInitialise(VL53LX_DEV pdev, uint8_t comms_type, uint16_t comms_speed_khz)
{
  return VL53LX_ERROR_NONE;
}

VL53LX_Error VL53LX_CommsClose(VL53LX_DEV pdev)
{
  return VL53LX_ERROR_NONE;
}