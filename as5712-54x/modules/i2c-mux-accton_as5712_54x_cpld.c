/*
 * I2C multiplexer
 *
 * Copyright (C)  Brandon Chuang <brandon_chuang@accton.com.tw>
 *
 * This module supports the accton cpld that hold the channel select
 * mechanism for other i2c slave devices, such as SFP.
 * This includes the:
 *	 Accton as5712_54x CPLD1/CPLD2/CPLD3
 *
 * Based on:
 *	pca954x.c from Kumar Gala <galak@kernel.crashing.org>
 * Copyright (C) 2006
 *
 * Based on:
 *	pca954x.c from Ken Harrenstien
 * Copyright (C) 2004 Google, Inc. (Ken Harrenstien)
 *
 * Based on:
 *	i2c-virtual_cb.c from Brian Kuschak <bkuschak@yahoo.com>
 * and
 *	pca9540.c from Jean Delvare <khali@linux-fr.org>.
 *
 * This file is licensed under the terms of the GNU General Public
 * License version 2. This program is licensed "as is" without any
 * warranty of any kind, whether express or implied.
 */
#if 0
#define DEBUG
#endif

#include <linux/module.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/device.h>
#include <linux/i2c.h>
#include <linux/i2c-mux.h>
#include <linux/dmi.h>
#include <linux/version.h>

static struct dmi_system_id as5712_dmi_table[] = {
    {
        .ident = "Accton AS5712",
        .matches = {
            DMI_MATCH(DMI_BOARD_VENDOR, "Accton"),
            DMI_MATCH(DMI_PRODUCT_NAME, "AS5712"),
        },
    },
    {
        .ident = "Accton AS5712",
        .matches = {
            DMI_MATCH(DMI_SYS_VENDOR, "Accton"),
            DMI_MATCH(DMI_PRODUCT_NAME, "AS5712"),
        },
    },
};

int platform_accton_as5712_54x(void)
{
    return dmi_check_system(as5712_dmi_table);
}
EXPORT_SYMBOL(platform_accton_as5712_54x);

#define NUM_OF_CPLD1_CHANS 0x0
#define NUM_OF_CPLD2_CHANS 0x18
#define NUM_OF_CPLD3_CHANS 0x1E
#define CPLD_CHANNEL_SELECT_REG 0x2
#define CPLD_DESELECT_CHANNEL   0xFF

#if 0
#define NUM_OF_ALL_CPLD_CHANS (NUM_OF_CPLD2_CHANS + NUM_OF_CPLD3_CHANS)
#endif

#define ACCTON_I2C_CPLD_MUX_MAX_NCHANS  NUM_OF_CPLD3_CHANS

static LIST_HEAD(cpld_client_list);
static struct mutex     list_lock;

struct cpld_client_node {
    struct i2c_client *client;
    struct list_head   list;
};

enum cpld_mux_type {
    as5712_54x_cpld2,
    as5712_54x_cpld3,
    as5712_54x_cpld1
};

struct accton_i2c_cpld_mux {
    enum cpld_mux_type type;
    struct i2c_adapter *virt_adaps[ACCTON_I2C_CPLD_MUX_MAX_NCHANS];
    u8 last_chan;  /* last register value */
#if LINUX_VERSION_CODE >= KERNEL_VERSION(4,7,0)
    struct i2c_client *client;
    struct i2c_mux_core *muxc;
#endif
};

#if 0
/* The mapping table between mux index and adapter index
   array index : the mux index
   the content : adapter index
 */
static int mux_adap_map[NUM_OF_ALL_CPLD_CHANS];
#endif

struct chip_desc {
    u8   nchans;
    u8   deselectChan;
};

/* Provide specs for the PCA954x types we know about */
static const struct chip_desc chips[] = {
    [as5712_54x_cpld1] = {
        .nchans        = NUM_OF_CPLD1_CHANS,
        .deselectChan  = CPLD_DESELECT_CHANNEL,
    },
    [as5712_54x_cpld2] = {
        .nchans        = NUM_OF_CPLD2_CHANS,
        .deselectChan  = CPLD_DESELECT_CHANNEL,
    },
    [as5712_54x_cpld3] = {
        .nchans        = NUM_OF_CPLD3_CHANS,
        .deselectChan  = CPLD_DESELECT_CHANNEL,
    }
};

static const struct i2c_device_id accton_i2c_cpld_mux_id[] = {
    { "as5712_54x_cpld1", as5712_54x_cpld1 },
    { "as5712_54x_cpld2", as5712_54x_cpld2 },
    { "as5712_54x_cpld3", as5712_54x_cpld3 },
    { }
};
MODULE_DEVICE_TABLE(i2c, accton_i2c_cpld_mux_id);

/* Write to mux register. Don't use i2c_transfer()/i2c_smbus_xfer()
   for this as they will try to lock adapter a second time */
static int accton_i2c_cpld_mux_reg_write(struct i2c_adapter *adap,
        struct i2c_client *client, u8 val)
{
#if 0
    int ret = -ENODEV;

    //if (adap->algo->master_xfer) {
    if (0)
        struct i2c_msg msg;
    char buf[2];

    msg.addr = client->addr;
    msg.flags = 0;
    msg.len = 2;
    buf[0] = 0x2;
    buf[1] = val;
    msg.buf = buf;
    ret = adap->algo->master_xfer(adap, &msg, 1);
}
else {
    union i2c_smbus_data data;
    ret = adap->algo->smbus_xfer(adap, client->addr,
                                 client->flags,
                                 I2C_SMBUS_WRITE,
                                 0x2, I2C_SMBUS_BYTE, &data);
}

return ret;
#else
    unsigned long orig_jiffies;
    unsigned short flags;
    union i2c_smbus_data data;
    int try;
    s32 res = -EIO;

    data.byte = val;
    flags = client->flags;
    flags &= I2C_M_TEN | I2C_CLIENT_PEC;

    if (adap->algo->smbus_xfer) {
        /* Retry automatically on arbitration loss */
        orig_jiffies = jiffies;
        for (res = 0, try = 0; try <= adap->retries; try++) {
                        res = adap->algo->smbus_xfer(adap, client->addr, flags,
                                                     I2C_SMBUS_WRITE, CPLD_CHANNEL_SELECT_REG,
                                                     I2C_SMBUS_BYTE_DATA, &data);
                        if (res != -EAGAIN)
                            break;
                        if (time_after(jiffies,
                                       orig_jiffies + adap->timeout))
                            break;
                    }
    }

    return res;
#endif
}

#if LINUX_VERSION_CODE >= KERNEL_VERSION(4,7,0)
static int accton_i2c_cpld_mux_select_chan(struct i2c_mux_core *muxc,
        u32 chan)
{
    struct accton_i2c_cpld_mux *data = i2c_mux_priv(muxc);
    struct i2c_client *client = data->client;
    u8 regval;
    int ret = 0;
    regval = chan;

    /* Only select the channel if its different from the last channel */
    if (data->last_chan != regval) {
        ret = accton_i2c_cpld_mux_reg_write(muxc->parent, client, regval);
        data->last_chan = regval;
    }

    return ret;
}

static int accton_i2c_cpld_mux_deselect_mux(struct i2c_mux_core *muxc,
        u32 chan)
{
    struct accton_i2c_cpld_mux *data = i2c_mux_priv(muxc);
    struct i2c_client *client = data->client;

    /* Deselect active channel */
    data->last_chan = chips[data->type].deselectChan;

    return accton_i2c_cpld_mux_reg_write(muxc->parent, client, data->last_chan);
}
#else

static int accton_i2c_cpld_mux_select_chan(struct i2c_adapter *adap,
			       void *client, u32 chan)
{
	struct accton_i2c_cpld_mux *data = i2c_get_clientdata(client);
	u8 regval;
	int ret = 0;
    regval = chan;

	/* Only select the channel if its different from the last channel */
	if (data->last_chan != regval) {
		ret = accton_i2c_cpld_mux_reg_write(adap, client, regval);
		data->last_chan = regval;
	}

	return ret;
}

static int accton_i2c_cpld_mux_deselect_mux(struct i2c_adapter *adap,
				void *client, u32 chan)
{
	struct accton_i2c_cpld_mux *data = i2c_get_clientdata(client);

	/* Deselect active channel */
	data->last_chan = chips[data->type].deselectChan;

	return accton_i2c_cpld_mux_reg_write(adap, client, data->last_chan);
}

#endif /*#if LINUX_VERSION_CODE >= KERNEL_VERSION(4,7,0)*/

static void accton_i2c_cpld_add_client(struct i2c_client *client)
{
    struct cpld_client_node *node = kzalloc(sizeof(struct cpld_client_node), GFP_KERNEL);

    if (!node) {
        dev_dbg(&client->dev, "Can't allocate cpld_client_node (0x%x)\n", client->addr);
        return;
    }

    node->client = client;

    mutex_lock(&list_lock);
    list_add(&node->list, &cpld_client_list);
    mutex_unlock(&list_lock);
}

static void accton_i2c_cpld_remove_client(struct i2c_client *client)
{
    struct list_head    *list_node = NULL;
    struct cpld_client_node *cpld_node = NULL;
    int found = 0;

    mutex_lock(&list_lock);

    list_for_each(list_node, &cpld_client_list)
    {
        cpld_node = list_entry(list_node, struct cpld_client_node, list);

        if (cpld_node->client == client) {
            found = 1;
            break;
        }
    }

    if (found) {
        list_del(list_node);
        kfree(cpld_node);
    }

    mutex_unlock(&list_lock);
}

static ssize_t show_cpld_version(struct device *dev, struct device_attribute *attr, char *buf)
{
    u8 reg = 0x1;
    struct i2c_client *client;
    int len;

    client = to_i2c_client(dev);
    len = sprintf(buf, "%d", i2c_smbus_read_byte_data(client, reg));

    return len;
}

static struct device_attribute ver = __ATTR(version, 0600, show_cpld_version, NULL);

/*
 * I2C init/probing/exit functions
 */
static int accton_i2c_cpld_mux_probe(struct i2c_client *client,
                                     const struct i2c_device_id *id)
{
    struct i2c_adapter *adap = to_i2c_adapter(client->dev.parent);
    struct accton_i2c_cpld_mux *data;
#if LINUX_VERSION_CODE >= KERNEL_VERSION(4,7,0)
    int force, class;
    struct i2c_mux_core *muxc;
#endif
    int chan=0;
    int ret = -ENODEV;

    if (!i2c_check_functionality(adap, I2C_FUNC_SMBUS_BYTE))
        goto err;
#if LINUX_VERSION_CODE >= KERNEL_VERSION(4,7,0)
    muxc = i2c_mux_alloc(adap, &client->dev,
                         chips[id->driver_data].nchans,
                         sizeof(*data), 0,
                         accton_i2c_cpld_mux_select_chan,
                         accton_i2c_cpld_mux_deselect_mux);
    if (!muxc)
        return -ENOMEM;

    data = i2c_mux_priv(muxc);
    i2c_set_clientdata(client, data);
    data->muxc = muxc;
    data->client = client;
#else

    data = devm_kzalloc(&client->dev,
                        sizeof(struct accton_i2c_cpld_mux), GFP_KERNEL);
    if (!data) {
        ret = -ENOMEM;
        goto err;
    }
    i2c_set_clientdata(client, data);
#endif

    data->type = id->driver_data;

    if (data->type == as5712_54x_cpld2 || data->type == as5712_54x_cpld3) {
        data->last_chan = chips[data->type].deselectChan; /* force the first selection */

        /* Now create an adapter for each channel */
        for (chan = 0; chan < chips[data->type].nchans; chan++) {
#if LINUX_VERSION_CODE >= KERNEL_VERSION(4,7,0)
            force = 0;			  /* dynamic adap number */
            class = 0;			  /* no class by default */
            ret = i2c_mux_add_adapter(muxc, force, chan, class);
            if (ret)
#else
            data->virt_adaps[chan] = i2c_add_mux_adapter(adap, &client->dev, client, 0, chan,
                                     0,
                                     accton_i2c_cpld_mux_select_chan,
                                     accton_i2c_cpld_mux_deselect_mux);
            if (data->virt_adaps[chan] == NULL)
#endif
            {
                ret = -ENODEV;
                dev_err(&client->dev, "failed to register multiplexed adapter %d\n", chan);
                goto virt_reg_failed;
            }
        }

        dev_info(&client->dev, "registered %d multiplexed busses for I2C mux %s\n",
                 chan, client->name);
    }

    accton_i2c_cpld_add_client(client);

    ret = sysfs_create_file(&client->dev.kobj, &ver.attr);
    if (ret)
        goto virt_reg_failed;

    return 0;

virt_reg_failed:
#if LINUX_VERSION_CODE >= KERNEL_VERSION(4,7,0)
    i2c_mux_del_adapters(muxc);
#else
    for (chan--; chan >= 0; chan--) {
        i2c_del_mux_adapter(data->virt_adaps[chan]);
    }
#endif
err:
    return ret;
}

static int accton_i2c_cpld_mux_remove(struct i2c_client *client)
{
    struct accton_i2c_cpld_mux *data = i2c_get_clientdata(client);
#if LINUX_VERSION_CODE >= KERNEL_VERSION(4,7,0)
    struct i2c_mux_core *muxc = data->muxc;

    i2c_mux_del_adapters(muxc);
#else
    const struct chip_desc *chip = &chips[data->type];
    int chan;

    for (chan = 0; chan < chip->nchans; ++chan) {
        if (data->virt_adaps[chan]) {
            i2c_del_mux_adapter(data->virt_adaps[chan]);
            data->virt_adaps[chan] = NULL;
        }
    }
#endif
    sysfs_remove_file(&client->dev.kobj, &ver.attr);
    accton_i2c_cpld_remove_client(client);

    return 0;
}

int as5712_54x_i2c_cpld_read(unsigned short cpld_addr, u8 reg)
{
    struct list_head   *list_node = NULL;
    struct cpld_client_node *cpld_node = NULL;
    int ret = -EPERM;

    mutex_lock(&list_lock);

    list_for_each(list_node, &cpld_client_list)
    {
        cpld_node = list_entry(list_node, struct cpld_client_node, list);

        if (cpld_node->client->addr == cpld_addr) {
            ret = i2c_smbus_read_byte_data(cpld_node->client, reg);
            break;
        }
    }

    mutex_unlock(&list_lock);

    return ret;
}
EXPORT_SYMBOL(as5712_54x_i2c_cpld_read);

int as5712_54x_i2c_cpld_write(unsigned short cpld_addr, u8 reg, u8 value)
{
    struct list_head   *list_node = NULL;
    struct cpld_client_node *cpld_node = NULL;
    int ret = -EIO;

    mutex_lock(&list_lock);

    list_for_each(list_node, &cpld_client_list)
    {
        cpld_node = list_entry(list_node, struct cpld_client_node, list);

        if (cpld_node->client->addr == cpld_addr) {
            ret = i2c_smbus_write_byte_data(cpld_node->client, reg, value);
            break;
        }
    }

    mutex_unlock(&list_lock);

    return ret;
}
EXPORT_SYMBOL(as5712_54x_i2c_cpld_write);

#if 0
int accton_i2c_cpld_mux_get_index(int adap_index)
{
    int i;

    for (i = 0; i < NUM_OF_ALL_CPLD_CHANS; i++) {
        if (mux_adap_map[i] == adap_index) {
            return i;
        }
    }

    return -EINVAL;
}
EXPORT_SYMBOL(accton_i2c_cpld_mux_get_index);
#endif

static struct i2c_driver accton_i2c_cpld_mux_driver = {
    .driver		= {
        .name	= "as5712_54x_cpld",
        .owner	= THIS_MODULE,
    },
    .probe		= accton_i2c_cpld_mux_probe,
    .remove		= accton_i2c_cpld_mux_remove,
    .id_table	= accton_i2c_cpld_mux_id,
};

static int __init accton_i2c_cpld_mux_init(void)
{
    mutex_init(&list_lock);
    return i2c_add_driver(&accton_i2c_cpld_mux_driver);
}

static void __exit accton_i2c_cpld_mux_exit(void)
{
    i2c_del_driver(&accton_i2c_cpld_mux_driver);
}

MODULE_AUTHOR("Brandon Chuang <brandon_chuang@accton.com.tw>");
MODULE_DESCRIPTION("Accton I2C CPLD mux driver");
MODULE_LICENSE("GPL");

module_init(accton_i2c_cpld_mux_init);
module_exit(accton_i2c_cpld_mux_exit);
