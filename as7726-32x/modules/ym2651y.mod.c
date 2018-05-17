#include <linux/module.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

MODULE_INFO(vermagic, VERMAGIC_STRING);

__visible struct module __this_module
__attribute__((section(".gnu.linkonce.this_module"))) = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

static const struct modversion_info ____versions[]
__used
__attribute__((section("__versions"))) = {
	{ 0x533a1566, __VMLINUX_SYMBOL_STR(module_layout) },
	{ 0x959a84fd, __VMLINUX_SYMBOL_STR(i2c_del_driver) },
	{ 0x904d0224, __VMLINUX_SYMBOL_STR(i2c_register_driver) },
	{ 0xbe83ca86, __VMLINUX_SYMBOL_STR(hwmon_device_register) },
	{ 0x40defe54, __VMLINUX_SYMBOL_STR(sysfs_create_group) },
	{ 0xef3867d, __VMLINUX_SYMBOL_STR(_dev_info) },
	{ 0x2e51823, __VMLINUX_SYMBOL_STR(__mutex_init) },
	{ 0x20705009, __VMLINUX_SYMBOL_STR(kmem_cache_alloc_trace) },
	{ 0x8733c9e1, __VMLINUX_SYMBOL_STR(kmalloc_caches) },
	{ 0xaaa1b518, __VMLINUX_SYMBOL_STR(i2c_smbus_write_word_data) },
	{ 0x1b17e06c, __VMLINUX_SYMBOL_STR(kstrtoll) },
	{ 0x91715312, __VMLINUX_SYMBOL_STR(sprintf) },
	{ 0x14638468, __VMLINUX_SYMBOL_STR(i2c_smbus_read_word_data) },
	{ 0x7e149286, __VMLINUX_SYMBOL_STR(mutex_unlock) },
	{ 0x9166fada, __VMLINUX_SYMBOL_STR(strncpy) },
	{ 0xe4982bef, __VMLINUX_SYMBOL_STR(__dynamic_dev_dbg) },
	{ 0xdafdab1f, __VMLINUX_SYMBOL_STR(i2c_smbus_read_byte_data) },
	{ 0x7d11c268, __VMLINUX_SYMBOL_STR(jiffies) },
	{ 0xbe2bdb48, __VMLINUX_SYMBOL_STR(mutex_lock) },
	{ 0xdbbeeaca, __VMLINUX_SYMBOL_STR(i2c_smbus_read_i2c_block_data) },
	{ 0x37a0cba, __VMLINUX_SYMBOL_STR(kfree) },
	{ 0xbe4537c9, __VMLINUX_SYMBOL_STR(sysfs_remove_group) },
	{ 0x6f4078bc, __VMLINUX_SYMBOL_STR(hwmon_device_unregister) },
	{ 0xbdfb6dbb, __VMLINUX_SYMBOL_STR(__fentry__) },
};

static const char __module_depends[]
__used
__attribute__((section(".modinfo"))) =
"depends=i2c-core";

MODULE_ALIAS("i2c:ym2651");
