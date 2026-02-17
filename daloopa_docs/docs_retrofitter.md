---
title: Retrofitter
url: https://docs.daloopa.com/docs/retrofitter
path: /docs/retrofitter
---

# Retrofitter

# Retrofitter

Fit our links into your existing models. Update your personal models with Daloopa.

> 📘
> 
> ### 
> 
> What is Retrofitter?
> 
> Retrofitter is used to integrate an existing model into the Daloopa system by inserting the hyperlinks into cells. This provides auditability features and allows for the use of the Updater. **Retrofitter is accessed through the Daloopa Excel plugin.**

  


![](https://files.readme.io/b93fbc2-image.png)

  


## 

How Retrofitter Works

Retrofitter works by comparing a value in the target model to values in our database for a given period for a given company. It makes this match based on the value of the datapoint and does not currently use the row label in making a match.

Retrofitter has two optional functions that speed up the process of linking the model.

![](https://files.readme.io/a0b7cde-image.png)

  


## 

a. Auto Map / Manual Map

First is the **Auto Map** feature (this is the default setting).  
Auto Map is used when there are multiple instances of the same datapoint.

For example, our database might have multiple versions of Total Revenue for a given quarter. Auto Map will link to the first version of that datapoint (i.e., the one that is updated first). Turning off Auto Map will result in the user needing to manually choose each version of the datapoint.

**Recommended:** Toggle the first button to **Manual Map** to map the data links yourself.

This way you can make sure that each datapoint is correctly mapped to exactly where you want it to go.

![](https://files.readme.io/81a7d91-image.png)

  


For time-series where there is a unique map between your models and the company's disclosure, we will automatically map. For time-series where your data is found in multiple instances in the company disclosures, we will provide you with choices to perform the map.

For example, if you are mapping revenue, the company could have disclosed that time-series in both segmental breakdown and income statement.

  


## 

c. Unit Shift

The **Unit Shift** functionality checks to see if a datapoint was possibly either multiplied or divided by one thousand or one million.  
As an example, if a company reports revenue of $505,143 and this is in thousands, a user might instead enter it in their model in millions, or as $505.143. If Unit Shift is turned on, Retrofitter will return this as a possible match.

![](https://files.readme.io/9f02537-image.png)

  


## 

d. Sign Shift

Similarly, **Sign Shift** looks for instances where a user may have entered a value with a different sign than the company reported.  
This typically happens with expenses. As an example, if a company reported an R&D expense of $102,311 in thousands, a user might enter it in their model as -$102,311. Unit shift looks for instances like this and returns them as a potential match.

![](https://files.readme.io/f5aba98-image.png)

> 📘
> 
> Having both Unit and Sign shift selected will look for all combinations of unit (multiply and divide by thousands and millions) and sign (positive and negative) shifts. **

  


## 

e. Retrofit Formulas

If you have a cell with a formula, say "=E5+E6" with the values "10+15=25", retrofitting when the button is on (Retrofit Formulas) will replace that formula with a hardcoded 25 and insert a hyperlink.

You lose the formula, but gain the hyperlink which allows you to update that formula data.

However, if all the cells that feed into that formula have been retrofitted, then you can simply leave the formula alone.

> 📘
> 
> All maps will be technically correct; the choice is simply so you can map the location of the source to your data. If this is not important to you, simply turn on "Auto Map" and skip this step of manual mapping.

  


## 

f. Right-Click Retrofit

Alternatively, you can select a cell (or a group of cells) and use right-click to activate the Retrofitter.

When done this way, make sure **Update Columns** is toggled to **Update Cells**. This will restrict the retrofitting to only the cells you have selected.

![](https://files.readme.io/8bdb0fb-rclick.JPG)

  


## 

How to Use Retrofitter

In addition to the example below, please see [this video](https://youtu.be/smUB76NzMIQ) for an introduction to using Retrofitter.

  


> ❗️
> 
> ### 
> 
> Be careful!
> 
> Make sure you are retrofitting a column of **historical** data. Retrofitter maps your data to the company's disclosures. Do not map your column of forecasts, there will be no matches.

__Updated 9 days ago

* * *

[Getting started with Daloopa for Excel](/docs/getting-started)[Updater](/docs/updater)

Ask AI

