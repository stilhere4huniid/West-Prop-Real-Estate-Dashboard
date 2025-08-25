import streamlit_authenticator as stauth
hashed_passwords = stauth.Hasher(['adonis2025', 'takudzwa2025']).generate()
print(hashed_passwords)