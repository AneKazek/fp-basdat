-- Created by Redgate Data Modeler (https://datamodeler.redgate-platform.com)
-- Last modification date: 2025-11-27 15:43:57.264

-- tables
-- Table: network
CREATE TABLE network (
    network_id int  NOT NULL AUTO_INCREMENT,
    name varchar(50)  NOT NULL,
    chain_id int  NOT NULL,
    symbol_native varchar(10)  NULL DEFAULT 'eth',
    explorer_url varchar(200)  NULL,
    api_base_url varchar(200)  NULL,
    UNIQUE INDEX uk_chain_id (chain_id),
    CONSTRAINT network_pk PRIMARY KEY (network_id)
) ENGINE InnoDB;

-- Table: sync_log
CREATE TABLE sync_log (
    sync_id int  NOT NULL AUTO_INCREMENT,
    wallet_id int  NOT NULL,
    network_id int  NOT NULL,
    synced_at datetime  NULL DEFAULT current_timestamp,
    from_block bigint  NULL,
    to_block bigint  NULL,
    new_tx_count int  NULL DEFAULT 0,
    status varchar(50)  NULL DEFAULT 'success',
    CONSTRAINT sync_log_pk PRIMARY KEY (sync_id)
) ENGINE InnoDB;

-- Table: transaction
CREATE TABLE transaction (
    tx_id int  NOT NULL AUTO_INCREMENT,
    network_id int  NOT NULL,
    wallet_id int  NOT NULL,
    tx_hash char(66)  NOT NULL,
    block_number bigint  NOT NULL,
    time_stamp datetime  NOT NULL,
    from_address char(42)  NOT NULL,
    to_address char(42)  NULL,
    value_eth decimal(38,18)  NULL DEFAULT 0,
    gas_used bigint  NULL DEFAULT 0,
    tx_fee_eth decimal(38,18)  NULL DEFAULT 0,
    direction enum('in','out','self')  NOT NULL,
    status varchar(20)  NULL DEFAULT 'success',
    CONSTRAINT transaction_pk PRIMARY KEY (tx_id)
) ENGINE InnoDB;

CREATE INDEX idx_hash ON transaction (tx_hash);

CREATE INDEX idx_time ON transaction (time_stamp);

-- Table: user
CREATE TABLE user (
    user_id int  NOT NULL AUTO_INCREMENT,
    nrp varchar(20)  NULL,
    nama varchar(100)  NOT NULL,
    email varchar(100)  NULL,
    created_at datetime  NULL DEFAULT current_timestamp,
    UNIQUE INDEX uk_nrp (nrp),
    CONSTRAINT user_pk PRIMARY KEY (user_id)
) ENGINE InnoDB;

-- Table: wallet
CREATE TABLE wallet (
    wallet_id int  NOT NULL AUTO_INCREMENT,
    user_id int  NOT NULL,
    network_id int  NOT NULL,
    address char(42)  NOT NULL,
    label varchar(100)  NULL DEFAULT 'main wallet',
    created_at datetime  NULL DEFAULT current_timestamp,
    UNIQUE INDEX uk_wallet_net (network_id,address),
    CONSTRAINT wallet_pk PRIMARY KEY (wallet_id)
) ENGINE InnoDB;

-- foreign keys
-- Reference: FK_0 (table: wallet)
ALTER TABLE wallet ADD CONSTRAINT FK_0 FOREIGN KEY FK_0 (user_id)
    REFERENCES user (user_id)
    ON DELETE CASCADE;

-- Reference: FK_1 (table: wallet)
ALTER TABLE wallet ADD CONSTRAINT FK_1 FOREIGN KEY FK_1 (network_id)
    REFERENCES network (network_id)
    ON DELETE RESTRICT;

-- Reference: FK_2 (table: transaction)
ALTER TABLE transaction ADD CONSTRAINT FK_2 FOREIGN KEY FK_2 (network_id)
    REFERENCES network (network_id);

-- Reference: FK_3 (table: transaction)
ALTER TABLE transaction ADD CONSTRAINT FK_3 FOREIGN KEY FK_3 (wallet_id)
    REFERENCES wallet (wallet_id)
    ON DELETE CASCADE;

-- Reference: FK_4 (table: sync_log)
ALTER TABLE sync_log ADD CONSTRAINT FK_4 FOREIGN KEY FK_4 (wallet_id)
    REFERENCES wallet (wallet_id)
    ON DELETE CASCADE;

-- Reference: FK_5 (table: sync_log)
ALTER TABLE sync_log ADD CONSTRAINT FK_5 FOREIGN KEY FK_5 (network_id)
    REFERENCES network (network_id);

-- End of file.

