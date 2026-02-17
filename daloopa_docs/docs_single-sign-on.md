---
title: Single Sign-On
url: https://docs.daloopa.com/docs/single-sign-on
path: /docs/single-sign-on
---

# Single Sign-On

# Single Sign-On

This guide walks you through connecting our authentication app to your Microsoft Entra (Azure AD) directory, enabling your users to sign in with Single Sign-On (SSO).

## 

Prerequisites

  * Admin access to your Microsoft Entra portal.



* * *

## 

Step 1: Sign in to Microsoft Entra Portal

  1. Go to the [Microsoft Entra Portal](https://entra.microsoft.com).
  2. Log in with your administrator account.



* * *

## 

Step 2: Register a New Application

  1. Navigate to **Azure Active Directory** > **App registrations**.
  2. Click **New registration**.
  3. Enter a **Name** for the app (e.g., "Daloopa Auth").
  4. Set **Supported account types** to "Accounts in this organizational directory only."
  5. Enter the **Redirect URI** (SPA) provided of our app: `https://auth.daloopa.com`
  6. Click **Register**.

![](https://files.readme.io/a03d5fffa0836c4d74ee8a43915a888d77bd325521552eee116325d966377322-image.png)

* * *

## 

Step 3: Configure API Permissions

  1. Select your newly registered app from the “App registrations” list.
  2. Go to **API permissions** > **Add a permission**.
  3. Choose **Microsoft Graph** > **Delegated permissions**.
  4. Add the following permissions:
     * `openid`
     * `profile`
     * `email`
  5. Click **Add permissions**.
  6. Click **Grant admin consent for [Your Org]** and confirm.

![](https://files.readme.io/2106930641be5ed78df12b81fa7ba549b7ac2d8dc4d237fb48db4350c62d89d2-image.png)

* * *

## 

Step 4: Configure Authentication options

  1. Navigate to **Authentication**.
  2. Under **Implicit grant and hybrid flows** , enable the following:
     1. Access tokens (used for implicit flows)
     2. ID tokens (used for implicit and hybrid flows)
  3. Under **Advanced settings** > **Allow public client flows** , select **Yes** for **Enable the following mobile and desktop flows**.
  4. Save the configuration.

![](https://files.readme.io/7b3a28d4a2bf35d57374f39716784bdb670758375a93a9638f60baafb13e738e-image.png)

* * *

## 

Step 5: Share the App Essentials

  1. Navigate to **Overview**.

  2. Share the following values with your Daloopa representative or customer support:

     * **Directory (tenant) ID**.
     * **Application (client) ID**.

![](https://files.readme.io/b96c254de84c8eb4aa0b1f81f8594216ddad5c855d47eb8e2a20f1eb02c664da-image.png)

* * *

## 

Step 6: Test the SSO Integration

Once you've got confirmation that both **Tenant ID** and **Client ID** have been registered, you should have SSO access to all Daloopa applications.

  1. Navigate to <https://marketplace.daloopa.com>.
  2. Click login and then the **Sign in with Microsoft** button.
  3. You should be redirected to the Daloopa Auth page.
     1. Enter your work email and click **Continue with SSO**.
  4. You should be redirected to the Microsoft login page.
  5. Authenticate using your Entra credentials.
  6. After successful login, you’ll be redirected back to the app.



* * *

## 

Troubleshooting Tips

  * Ensure Redirect URI in Entra matches exactly with Daloopa's Auth page.
  * Confirm API permissions are granted admin consent.
  * Check that both Access and ID tokens have been granted.
  * Verify tenant and client IDs are correctly entered.



* * *

For further assistance, please contact our support team.

__Updated 3 months ago

* * *

What’s Next

  * [Coverage](/docs/coverage)
  * [Getting started with Daloopa for Excel](/docs/getting-started)



Ask AI

