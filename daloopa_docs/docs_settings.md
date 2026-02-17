---
title: Settings
url: https://docs.daloopa.com/docs/settings
path: /docs/settings
---

# Settings

# Settings

Unlock the full potential of your Daloopa Plugin

# 

There are 3 layers of settings

  * Retrofitter level
  * Inspector level
  * Plug-in level

  


# 

1\. Retrofitter Settings

![](https://files.readme.io/421c125-image.png)

> Do not change the Api Endpoint in settings

## 

Sign check

On = we will retrofit your data even if the sign is different from disclosed data. (e.g. company discloses -120 for COGS but you have 120 in your model)

Off = do not retrofit when sign is different

  


## 

Unit check

On = we will retrofit your data if unit is different from disclosed data. (e.g. company discloses 1,200 and you have 1.2)

Off = do not retrofit when unit is different

  


## 

Match fuzziness

We all make mistakes. Sometimes you have a typo that is off from company disclosure, or used a number when the company discloses something more precise. By increasing match fuzziness, you allow the retrofitter to increase search space to include numbers that are []% similar to what you have in the model. At 1% fuzziness, if the actual is 101 and you have 100 in your model, we will suggest 101 as a possible retrofit map.

  


# 

2\. Inspector Settings

The Inspector allows you to retrofit and update all in one, and audit your data v. company data. For more details, please read the [Inspector](https://docs.daloopa.com/docs/inspector) section.

  


All settings available here are similar to the plug-in wide settings with a few differences:

## 

Real Time Update (Beta)

> 👍
> 
> ### 
> 
> This has been the #1 requested for feature!

**On =** when you hit update, it will update for any data that we already have, even if the entire model is not updated. This means that you can update your model at ANY TIME after the earnings drops. We update data based on priorities (KPIs before IS before BS etc.) and you can see your KPIs and IS update in minutes.

You can click on this as soon as you like, clicking this after a few minutes will always give you more data. After the entire model is updated, you will still receive the same email notification as you typically will.

**Due to the speed of this, we expect a lower than usual accuracy rate of data. Accurate data will be refreshed with regular updates when all the data is ready. Any data that is populated prior to our regular updates (~1h) could be prone to error.**

This feature is meant to be used to push data faster prior to an earnings call.

**Off =** Model will not update until we have 100% updated our data

# 

3\. Plug-in Settings

## 

Hyperlink formula

On = Use [=HYPERLINK("xxxxxx","123")] in cells

Off = Hardcode data, and insert hyperlink as a background hyperlink (use CTRL+K) to view

> ❗
> 
> ### 
> 
> Turning On will speed up the plugin by ~50x v. turning it off if you have Bloomberg plugin.
> 
> On allows us to bypass Bloomberg.

If you want to remove the "=HYPERLINK()" after, you can right click and click "Remove Hyperlinks"

![](https://files.readme.io/1ccc45e-2.JPG)   


## 

Highlight Cells

ON = When you hit Update/Retrofit/Inspect it will highlight cells in Green/Red/Gray color.

If cell is successfully updated/retrofitted it highlights to Green.

If fundamental id is not found for cells that highlights to Red.

If any value contains formula with constant it highlights to Gray.

OFF = when you hit Update/Retrofit/Inspect it will not highlight cells.

  


## 

Skip Financial Year

ON = When you perform Update/Retrofit/Inspect and set "Previous Quarter Number" it will skip column that contains financial year.

OFF = When you perform Update/Retrofit/Inspect and set "Previous Quarter Number" it will not skip column that contains financial year.

  


## 

Use Proxy Off

 __Updated 9 months ago

* * *

[Inspector](/docs/inspector)[Supported Calendar Period Formats](/docs/supported-calendar-period-formats)

Ask AI

