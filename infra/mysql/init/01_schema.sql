-- =============================================================================
-- SmartParking Database Schema — MySQL 8.4 LTS (InnoDB, utf8mb4, UTC)
-- Executed automatically on first container start via Docker entrypoint.
-- All timestamps UTC DATETIME(3).  Money stored as integer paise.
-- =============================================================================

-- Migration tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version   INT          NOT NULL PRIMARY KEY,
    name      VARCHAR(255) NOT NULL,
    applied_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Users ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id             BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT PRIMARY KEY,
    email          VARCHAR(255)     NOT NULL,
    password_hash  VARCHAR(255)     NOT NULL,
    full_name      VARCHAR(255)     NOT NULL,
    phone          VARCHAR(20)      DEFAULT NULL,
    role           ENUM('DRIVER','OPERATOR','ADMIN') NOT NULL DEFAULT 'DRIVER',
    status         ENUM('ACTIVE','INACTIVE','SUSPENDED') NOT NULL DEFAULT 'ACTIVE',
    email_verified TINYINT(1)       NOT NULL DEFAULT 0,
    created_at     DATETIME(3)      NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at     DATETIME(3)      NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    UNIQUE KEY uq_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── User Preferences ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS preferences (
    id                    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id               BIGINT UNSIGNED NOT NULL,
    default_vehicle_type  ENUM('CAR','MOTORCYCLE','SUV','TRUCK','EV') DEFAULT 'CAR',
    preferred_facilities  JSON            DEFAULT NULL,
    max_walking_distance_m INT            DEFAULT NULL,
    max_budget_paise      INT             DEFAULT NULL,
    created_at            DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at            DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    UNIQUE KEY uq_preferences_user (user_id),
    CONSTRAINT fk_preferences_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Parking Locations ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS parking_locations (
    id                     BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    owner_id               BIGINT UNSIGNED NOT NULL,
    name                   VARCHAR(255)    NOT NULL,
    address                TEXT            NOT NULL,
    lat                    DECIMAL(10,8)   NOT NULL,
    lng                    DECIMAL(11,8)   NOT NULL,
    location_point         POINT           NOT NULL /*!80003 SRID 4326 */,
    operating_hours        JSON            NOT NULL COMMENT '{"mon":{"open":"08:00","close":"22:00"},...}',
    facilities             JSON            DEFAULT NULL COMMENT '["ev_charging","covered","cctv","disabled_access","valet"]',
    base_rate_paise        INT             NOT NULL DEFAULT 2000,
    min_rate_paise         INT             NOT NULL DEFAULT 1000,
    max_rate_paise         INT             NOT NULL DEFAULT 10000,
    rate_update_interval_min INT           NOT NULL DEFAULT 15,
    pay_at_venue           TINYINT(1)      NOT NULL DEFAULT 0,
    status                 ENUM('PENDING','APPROVED','REJECTED','SUSPENDED') NOT NULL DEFAULT 'PENDING',
    total_slots            INT             NOT NULL DEFAULT 0,
    created_at             DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at             DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    SPATIAL INDEX idx_location_point (location_point),
    INDEX idx_locations_owner (owner_id),
    INDEX idx_locations_status (status),
    CONSTRAINT fk_locations_owner FOREIGN KEY (owner_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Parking Slots ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS parking_slots (
    id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    location_id  BIGINT UNSIGNED NOT NULL,
    code         VARCHAR(20)     NOT NULL COMMENT 'e.g. A1, B12, EV-01',
    vehicle_type ENUM('CAR','MOTORCYCLE','SUV','TRUCK','EV') NOT NULL DEFAULT 'CAR',
    restrictions JSON            DEFAULT NULL,
    status       ENUM('ACTIVE','BLOCKED') NOT NULL DEFAULT 'ACTIVE',
    created_at   DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at   DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    UNIQUE KEY uq_slots_location_code (location_id, code),
    INDEX idx_slots_location_status (location_id, status),
    INDEX idx_slots_vehicle (vehicle_type),
    CONSTRAINT fk_slots_location FOREIGN KEY (location_id) REFERENCES parking_locations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Price Quotes ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS price_quotes (
    id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    slot_id       BIGINT UNSIGNED NOT NULL,
    start_at      DATETIME(3)     NOT NULL,
    end_at        DATETIME(3)     NOT NULL,
    total_paise   INT             NOT NULL,
    line_items    JSON            NOT NULL COMMENT '[{"label":"Base 2h","amount_paise":4000},...]',
    valid_until   DATETIME(3)     NOT NULL,
    rule_version  VARCHAR(50)     NOT NULL DEFAULT 'v1',
    created_at    DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_quotes_slot (slot_id),
    INDEX idx_quotes_valid (valid_until),
    CONSTRAINT fk_quotes_slot FOREIGN KEY (slot_id) REFERENCES parking_slots(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Bookings ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bookings (
    id                  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id             BIGINT UNSIGNED NOT NULL,
    slot_id             BIGINT UNSIGNED NOT NULL,
    quote_id            BIGINT UNSIGNED DEFAULT NULL,
    start_at            DATETIME(3)     NOT NULL,
    end_at              DATETIME(3)     NOT NULL,
    status              ENUM('PENDING_PAYMENT','CONFIRMED','CANCELLED','EXPIRED','COMPLETED','REFUNDED')
                            NOT NULL DEFAULT 'PENDING_PAYMENT',
    total_paise         INT             NOT NULL,
    hold_expires_at     DATETIME(3)     DEFAULT NULL,
    source              ENUM('MANUAL','CHAT','AUTO') NOT NULL DEFAULT 'MANUAL',
    idempotency_key     VARCHAR(255)    DEFAULT NULL,
    cancellation_reason TEXT            DEFAULT NULL,
    created_at          DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at          DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    UNIQUE KEY uq_bookings_idempotency (user_id, idempotency_key),
    INDEX idx_bookings_user_status (user_id, status),
    INDEX idx_bookings_slot_time (slot_id, start_at, end_at),
    INDEX idx_bookings_status_hold (status, hold_expires_at),
    INDEX idx_bookings_slot_status (slot_id, status),
    CONSTRAINT fk_bookings_user  FOREIGN KEY (user_id)  REFERENCES users(id),
    CONSTRAINT fk_bookings_slot  FOREIGN KEY (slot_id)  REFERENCES parking_slots(id),
    CONSTRAINT fk_bookings_quote FOREIGN KEY (quote_id) REFERENCES price_quotes(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Booking Blocks (double-booking prevention) ──────────────────────────────
-- Each booking occupies 15-minute blocks.  The UNIQUE constraint on
-- (slot_id, block_start) makes overlap impossible at the database level.
CREATE TABLE IF NOT EXISTS booking_blocks (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    slot_id     BIGINT UNSIGNED NOT NULL,
    block_start DATETIME(3)     NOT NULL COMMENT 'Start of 15-min block (UTC)',
    booking_id  BIGINT UNSIGNED NOT NULL,
    UNIQUE KEY uq_slot_block (slot_id, block_start),
    INDEX idx_blocks_booking (booking_id),
    CONSTRAINT fk_blocks_slot    FOREIGN KEY (slot_id)    REFERENCES parking_slots(id),
    CONSTRAINT fk_blocks_booking FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Payments ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS payments (
    id                   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    booking_id           BIGINT UNSIGNED NOT NULL,
    razorpay_order_id    VARCHAR(255)    DEFAULT NULL,
    razorpay_payment_id  VARCHAR(255)    DEFAULT NULL,
    amount_paise         INT             NOT NULL,
    currency             VARCHAR(3)      NOT NULL DEFAULT 'INR',
    status               ENUM('CREATED','CAPTURED','FAILED','REFUND_PENDING','REFUNDED','PARTIALLY_REFUNDED')
                             NOT NULL DEFAULT 'CREATED',
    refund_amount_paise  INT             DEFAULT NULL,
    refund_id            VARCHAR(255)    DEFAULT NULL,
    refund_status        VARCHAR(50)     DEFAULT NULL,
    created_at           DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at           DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    UNIQUE KEY uq_payments_razorpay_order   (razorpay_order_id),
    UNIQUE KEY uq_payments_razorpay_payment (razorpay_payment_id),
    INDEX idx_payments_booking (booking_id),
    INDEX idx_payments_status  (status),
    CONSTRAINT fk_payments_booking FOREIGN KEY (booking_id) REFERENCES bookings(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Webhook Events (idempotent processing) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS webhook_events (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    event_id    VARCHAR(255)    NOT NULL COMMENT 'Razorpay event ID',
    event_type  VARCHAR(100)    NOT NULL,
    payload     JSON            NOT NULL,
    processed_at DATETIME(3)   DEFAULT NULL,
    created_at  DATETIME(3)    NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    UNIQUE KEY uq_webhook_event (event_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Occupancy Records (for ML forecasting) ──────────────────────────────────
CREATE TABLE IF NOT EXISTS occupancy_records (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    location_id BIGINT UNSIGNED NOT NULL,
    ts          DATETIME(3)     NOT NULL,
    total_slots INT             NOT NULL DEFAULT 0,
    occupied    INT             NOT NULL DEFAULT 0,
    available   INT             NOT NULL DEFAULT 0,
    synthetic   TINYINT(1)      NOT NULL DEFAULT 0,
    created_at  DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_occupancy_location_ts (location_id, ts),
    CONSTRAINT fk_occupancy_location FOREIGN KEY (location_id) REFERENCES parking_locations(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Auto-Booking Rules ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS auto_booking_rules (
    id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id            BIGINT UNSIGNED NOT NULL,
    name               VARCHAR(255)    NOT NULL,
    rule               JSON            NOT NULL COMMENT 'area, vehicle, days, time_window, max_price, facilities',
    lead_time_minutes  INT             NOT NULL DEFAULT 60,
    weekly_booking_cap INT             NOT NULL DEFAULT 5,
    enabled            TINYINT(1)      NOT NULL DEFAULT 0,
    created_at         DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at         DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    INDEX idx_auto_rules_user    (user_id),
    INDEX idx_auto_rules_enabled (enabled),
    CONSTRAINT fk_auto_rules_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Auto-Booking Audit ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS auto_booking_audit (
    id                   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    rule_id              BIGINT UNSIGNED NOT NULL,
    user_id              BIGINT UNSIGNED NOT NULL,
    candidates_count     INT             NOT NULL DEFAULT 0,
    selected_slot_id     BIGINT UNSIGNED DEFAULT NULL,
    selected_location_id BIGINT UNSIGNED DEFAULT NULL,
    booking_id           BIGINT UNSIGNED DEFAULT NULL,
    scores               JSON            DEFAULT NULL,
    decision             ENUM('BOOKED','NO_CANDIDATES','PRICE_CAP_EXCEEDED',
                              'WEEKLY_CAP_EXCEEDED','OVERLAP','SLOT_TAKEN','ERROR') NOT NULL,
    decision_reason      TEXT            DEFAULT NULL,
    rule_snapshot        JSON            NOT NULL,
    created_at           DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_auto_audit_rule    (rule_id),
    INDEX idx_auto_audit_user    (user_id),
    INDEX idx_auto_audit_booking (booking_id),
    CONSTRAINT fk_auto_audit_rule FOREIGN KEY (rule_id) REFERENCES auto_booking_rules(id),
    CONSTRAINT fk_auto_audit_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Notifications ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS notifications (
    id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id    BIGINT UNSIGNED NOT NULL,
    type       VARCHAR(50)     NOT NULL,
    title      VARCHAR(255)    NOT NULL,
    message    TEXT            NOT NULL,
    is_read    TINYINT(1)      NOT NULL DEFAULT 0,
    data       JSON            DEFAULT NULL,
    created_at DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_notifications_user (user_id, is_read),
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Audit Log ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id       BIGINT UNSIGNED DEFAULT NULL,
    action        VARCHAR(100)    NOT NULL,
    resource_type VARCHAR(50)     NOT NULL,
    resource_id   BIGINT UNSIGNED DEFAULT NULL,
    details       JSON            DEFAULT NULL,
    ip_address    VARCHAR(45)     DEFAULT NULL,
    created_at    DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_audit_user     (user_id),
    INDEX idx_audit_resource (resource_type, resource_id),
    INDEX idx_audit_created  (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── System Configuration ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS system_config (
    config_key   VARCHAR(100) NOT NULL PRIMARY KEY,
    config_value JSON         NOT NULL,
    description  TEXT         DEFAULT NULL,
    updated_at   DATETIME(3)  NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Seed: initial migration record ──────────────────────────────────────────
INSERT INTO schema_migrations (version, name) VALUES (1, 'initial_schema');

-- ── Seed: default system configuration ──────────────────────────────────────
INSERT INTO system_config (config_key, config_value, description) VALUES
('hold_duration_minutes',    '10',
 'How long a PENDING_PAYMENT hold lasts before expiry'),
('min_duration_minutes',     '30',
 'Minimum booking duration in minutes'),
('max_duration_hours',       '24',
 'Maximum booking duration in hours'),
('booking_granularity_minutes', '15',
 'Time-block granularity for booking_blocks'),
('cancellation_policy',
 '{"full_refund_minutes_before": 60, "partial_refund_pct": 50, "no_refund_after_start": true}',
 'Cancellation refund policy'),
('pricing_bands',
 '{"low": {"max_occupancy_pct": 0.4, "multiplier": 1.0}, "medium": {"max_occupancy_pct": 0.75, "multiplier": 1.5}, "high": {"max_occupancy_pct": 1.0, "multiplier": 2.25}}',
 'Occupancy-based pricing band multipliers'),
('score_weights',
 '{"distance": 0.35, "price": 0.30, "availability": 0.15, "facilities": 0.20}',
 'Recommendation scoring weights'),
('per_user_pending_limit',   '3',
 'Maximum concurrent PENDING_PAYMENT bookings per user');

-- ── Read-only user for AI service ───────────────────────────────────────────
CREATE USER IF NOT EXISTS 'ai_reader'@'%' IDENTIFIED BY 'ai_reader_pass';
GRANT SELECT ON smart_parking.occupancy_records  TO 'ai_reader'@'%';
GRANT SELECT ON smart_parking.bookings           TO 'ai_reader'@'%';
GRANT SELECT ON smart_parking.booking_blocks     TO 'ai_reader'@'%';
GRANT SELECT ON smart_parking.parking_locations  TO 'ai_reader'@'%';
GRANT SELECT ON smart_parking.parking_slots      TO 'ai_reader'@'%';
GRANT SELECT ON smart_parking.system_config      TO 'ai_reader'@'%';
FLUSH PRIVILEGES;
