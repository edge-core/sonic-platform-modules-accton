ifneq ($(KERNELRELEASE),)
obj-m:= accton_wedge100bf_psensor.o
	    
else
ifeq (,$(KERNEL_SRC))
#$(error KERNEL_SRC is not defined)
KVERSION    := $(shell uname -r)
KERNEL_DIR   = /usr/src/linux-headers-$(KVERSION)/
KERNELDIR:=$(KERNEL_DIR)
#export KERNELDIR:=${PWD}/../../../../../src/sonic-linux-kernel/linux-3.16.43/
else
KERNELDIR:=$(KERNEL_SRC)
endif
PWD:=$(shell pwd)
default:
	$(MAKE) -C $(KERNELDIR)  M=$(PWD) modules
clean:
	rm -rf *.o *.mod.o *.mod.o *.ko .*cmd .tmp_versions Module.markers Module.symvers modules.order
endif
