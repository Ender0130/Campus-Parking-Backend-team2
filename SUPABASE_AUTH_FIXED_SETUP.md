# Supabase Auth Fixed Setup

This version uses Supabase Auth for real email/password accounts.

Important: Supabase Auth email confirmation needs email delivery. With the default Supabase mail server, emails may only go to project/team addresses and may be heavily rate limited. For real user email confirmation, configure Custom SMTP in Supabase.

## What changed

Frontend:
- Uses Supabase Auth instead of Flask /register and /login.
- Signup requires a real email address.
- The login page shows errors directly on the page instead of only using Alert popups.
- Includes an auth debug panel and a command-line auth test.

Backend:
- /lots, /report, and /me require a Supabase access token.
- Flask verifies the token with Supabase and uses the real Supabase user id for points.

## Required Supabase settings

Authentication -> Sign In / Providers:
- Allow new users to sign up: ON
- Email provider: Enabled
- Confirm email: ON

Authentication -> URL Configuration:
- Site URL: http://localhost:8081
- Redirect URLs:
  - http://localhost:8081/**
  - http://localhost:8081/login
  - http://localhost:8081/auth/confirm
  - campusparkingtracker://**

Authentication -> Email -> SMTP Settings:
- Enable Custom SMTP.
- You can use Resend, SendGrid, Brevo, Postmark, AWS SES, etc.
- Example Resend values:
  - Host: smtp.resend.com
  - Port: 465
  - Username: resend
  - Password: your Resend API key
  - Sender email: an email address on your verified Resend domain
  - Sender name: Campus Parking Tracker

## Backend .env

Create this file:

Campus-Parking-Backend-team2-main/.env

Contents:

SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
SUPABASE_PUBLISHABLE_KEY=YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY

## Frontend .env

Create this file:

campus-parking-tracker-team2-main/campusparkingtracker/.env

Contents for web:

EXPO_PUBLIC_API_BASE_URL=http://127.0.0.1:5001
EXPO_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY=YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY
EXPO_PUBLIC_AUTH_REDIRECT_URL=http://localhost:8081/login

## Test Supabase auth outside the app

From the frontend folder, after npm install:

npm run auth:test -- signup yourrealemail@example.com Password123

If this fails with Email address not authorized, Custom SMTP is not configured correctly in Supabase.

If it says signup request accepted, check the inbox and spam folder. Then run:

npm run auth:test -- login yourrealemail@example.com Password123

Login works only after the email is confirmed.
