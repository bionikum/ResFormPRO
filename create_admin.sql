INSERT INTO users (email, name, role, is_active, password_hash)
VALUES (
    'admin@resformpro.ru',
    'Administrator',
    'admin',
    TRUE,
    'scrypt:32768:8:1$B6VatxKLGUpUpKdX$0cdb02d4ae7a0ee5d389da335751d264a3d457d9cf23c36dc43568e7a249e6855bcfee843a489ea64d59807980fd6c1221244a7d32f2cd4fbde7da0b8c4211b3'
)
ON CONFLICT (email) DO UPDATE SET
    name = EXCLUDED.name,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active,
    password_hash = EXCLUDED.password_hash;
