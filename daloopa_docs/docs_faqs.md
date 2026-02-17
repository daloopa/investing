---
title: FAQs
url: https://docs.daloopa.com/docs/faqs
path: /docs/faqs
---

# FAQs

# FAQs

## 

Do you cover international companies?

Yes, Daloopa has models for most major international companies. Including some companies that report in non-English languages.

  


## 

What happens with IPOs?

When a company files for an IPO, we will initiate a process to start building a model. Our IPO models will contain data going back as far as the filing discloses. In the US, we build our IPO models based off the S-1 and 424Bs.

We cover all major IPOs above an expected USD2bn and above valuation. If you would like to be sure that an IPO you are interested in is covered by us, please let us know and we will provide you with real-time deliverable updates.

  


## 

Does adding/deleting rows in your model mess it up?

No. Daloopa models are meant to be used in your normal course of Excel work. Feel free to add/delete rows, add formulas, copy the data out etc. Our data is hardcoded with a hyperlink attached, so you can transform and use the data as you wish.

  


## 

Will my model work offline?

Certainly. Daloopa models are meant to be used in any situation. However, do note that the source links bring you to a web portal hosted by us in the cloud, and the plugin fetches data from our database in the cloud. If you are offline, you will still have full access to all your data, but the links and plugin will only work when you are back online.

  


## 

What do the colors mean?

![817](https://files.readme.io/16e0c09-FAQ1.JPG)

Blue means a hardcoded number. These datapoints will always have a link to the source document.  
Black means a calculated number.

  


## 

Why are some "sums" calculated and some "sums" hardcoded?

In the previous example, 1,007.9 is hardcoded but 1,010.5 is calculated. The sum of the data above 1,007.9 does not get you to 1,007.9 due to rounding issues, therefore we provide you with the actual data disclosed. In the latter example, the sum equals the disclosed number. Therefore, we create a sum function within Excel. Both datapoints contain links to the source.

The column of data for 2013Q4 in this example is all calculated. This is because, in Q4, the company disclosed year-end data and not quarterly data. We obtain the quarterly data by subtracting Q1 to Q3 numbers from the year-end number.

  


## 

How do you deal with resegmentation and M&A?

![1215](https://files.readme.io/5c1ceb8-FAQ2.JPG)

In this case, when new data is disclosed, we add rows in the model and create new rows for newly disclosed data (Rows 392 to 408). For data that is no longer disclosed, we keep the old data in the model but will not continue updating.

  


## 

What if a company restates past numbers?

At Daloopa, we extract data as-is from the source document when it is disclosed. We will display data from the point it is first disclosed, and we do not display restated numbers. You can click on the latest quarter to check for restatements using our audit tool.

We are currently working on a private beta with some customers to offer a restated version of our models. Speak to your customer success representative to learn more about this beta.

  


## 

How are unit changes dealt with?

We display all units based on the latest unit disclosed. For instance, if a company were to change from thousands to millions, we will retroactively convert all units into millions in our model. Our updater and retrofitter are intelligent enough to handle units in your models that may not coincide with how the company discloses them. (ie. we will update your model in base millions, even if the company discloses in thousands)

  


## 

Why do your cash flow statement data differ from company disclosed data?

Often companies disclose cash flow data using "year-to-date" data and not "quarterly" data like the rest of the filing. We will perform the subtraction to provide you with the quarterly data. For example, the company might disclose [10,20,31,42] but we will provide [10,10,11,12]. When you click on [12], we will source you to [42].

  


## 

What if my data is not in the same units or sign as company disclosures?

Daloopa Retrofitter and Updater is smart enough to know when you are using different units and signs from the company's disclosure. This happens most often when a company discloses in **thousands** and you model in **millions** , or when a company provides a **negative** number for an expensive item, but you have it as a **positive** number in your model.

The following ~2min video will explain in detail how it works.

  


__Updated 9 days ago

* * *

[Navigating a model](/docs/navigating-a-model)[Click-Through Audit](/docs/one-click-audit)

Ask AI

