-- Schema for theminiceo Crypto Paywall D1 Database
-- Table: redeemed_transactions
-- Primary Key: tx_hash ensures ACID uniqueness and replay protection

CREATE TABLE IF NOT EXISTS redeemed_transactions (
    tx_hash TEXT PRIMARY KEY,
    network TEXT NOT NULL,
    book_id TEXT NOT NULL,
    email TEXT NOT NULL,
    sender_address TEXT NOT NULL,
    amount_raw TEXT NOT NULL,
    block_number INTEGER NOT NULL,
    redeemed_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_redeemed_book_email ON redeemed_transactions (book_id, email);
CREATE INDEX IF NOT EXISTS idx_redeemed_network_redeemed_at ON redeemed_transactions (network, redeemed_at);
