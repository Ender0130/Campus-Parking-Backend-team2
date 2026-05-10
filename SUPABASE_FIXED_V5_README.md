# Campus Parking Tracker Supabase Fixed V5

This is the fixed version for the specific problem where Supabase signup/login works, but the parking page fails because Flask returns 503 while trying to verify the Supabase token.

What changed from V3:

1. The frontend still signs up and logs in directly with Supabase Auth.
2. The frontend still sends Authorization: Bearer <Supabase access_token> to Flask.
3. Flask first tries the real Supabase Auth user endpoint.
4. If Python/Flask cannot reach or verify through Supabase locally, Flask falls back to reading the Supabase JWT payload for local development so the class project runs.
5. The backend includes /debug/auth so you can prove the token is accepted.
6. The frontend includes npm run api:test to test Supabase login, Flask auth, report submission, and lots loading before opening the web app.

Important:

- For local development, keep Confirm email OFF in Supabase.
- For production, set SUPABASE_LOCAL_DEV_FALLBACK=false and configure real server-side JWT verification or keep the Supabase Auth API verification working.
