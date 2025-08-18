ifneq ($(SYSTEMC_EXISTS),)
default: run
else
default: nosc
endif
