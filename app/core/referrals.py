import os
import sqlite3
from datetime import datetime
from pathlib import Path
from uuid import uuid4


# =========================================================
# ПУТЬ К БАЗЕ
# =========================================================

AMVERA_DATA_DIR = Path("/data")

if AMVERA_DATA_DIR.exists():
    DB_PATH = AMVERA_DATA_DIR / "as_estetik_referrals.db"
else:
    LOCAL_DATA_DIR = Path("data")
    LOCAL_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    DB_PATH = (
        LOCAL_DATA_DIR
        / "as_estetik_referrals.db"
    )


# =========================================================
# ПОДКЛЮЧЕНИЕ
# =========================================================

def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# СОЗДАНИЕ ТАБЛИЦ
# =========================================================

def init_referral_db() -> None:
    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS referral_partners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                bonus_percent INTEGER NOT NULL DEFAULT 10,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS referral_clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                platform TEXT NOT NULL,
                platform_user_id TEXT NOT NULL,

                username TEXT,
                first_name TEXT,

                ref_code TEXT,

                first_visit_paid INTEGER NOT NULL DEFAULT 0,
                bonus_amount INTEGER NOT NULL DEFAULT 0,
                bonus_paid INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL,
                paid_at TEXT,

                UNIQUE(
                    platform,
                    platform_user_id
                )
            )
            """
        )

        connection.commit()


# =========================================================
# ПАРТНЁР / РЕКОМЕНДАТЕЛЬ
# =========================================================

def add_referral_partner(
    code: str,
    name: str,
    bonus_percent: int = 10,
) -> None:

    normalized_code = (
        code
        .strip()
        .upper()
    )

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO referral_partners (
                code,
                name,
                bonus_percent,
                is_active,
                created_at
            )
            VALUES (?, ?, ?, 1, ?)

            ON CONFLICT(code)
            DO UPDATE SET
                name = excluded.name,
                bonus_percent = excluded.bonus_percent,
                is_active = 1
            """,
            (
                normalized_code,
                name.strip(),
                bonus_percent,
                datetime.now().isoformat(
                    timespec="seconds"
                ),
            ),
        )

        connection.commit()


def get_referral_partner(
    code: str,
):
    normalized_code = (
        code
        .strip()
        .upper()
    )

    with get_connection() as connection:

        return connection.execute(
            """
            SELECT *
            FROM referral_partners
            WHERE code = ?
              AND is_active = 1
            """,
            (
                normalized_code,
            ),
        ).fetchone()


def get_referral_partners():
    with get_connection() as connection:

        return connection.execute(
            """
            SELECT *
            FROM referral_partners
            WHERE is_active = 1
            ORDER BY name
            """
        ).fetchall()


# =========================================================
# НОВЫЙ КЛИЕНТ ПО РЕКОМЕНДАЦИИ
# =========================================================

def register_referral_client(
    platform: str,
    platform_user_id: str,
    ref_code: str,
    username: str | None = None,
    first_name: str | None = None,
) -> bool:

    normalized_code = (
        ref_code
        .strip()
        .upper()
    )

    partner = get_referral_partner(
        normalized_code
    )

    if not partner:
        return False

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO referral_clients (
                platform,
                platform_user_id,
                username,
                first_name,
                ref_code,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                platform,
                str(platform_user_id),
                username,
                first_name,
                normalized_code,
                datetime.now().isoformat(
                    timespec="seconds"
                ),
            ),
        )

        connection.commit()

    return cursor.rowcount > 0


# =========================================================
# РУЧНОЕ ДОБАВЛЕНИЕ КЛИЕНТА
# =========================================================

def add_manual_referral_client(
    first_name: str,
    ref_code: str,
) -> int:

    normalized_code = (
        ref_code
        .strip()
        .upper()
    )

    partner = get_referral_partner(
        normalized_code
    )

    if not partner:
        raise ValueError(
            "Рекомендатель не найден."
        )

    manual_user_id = (
        f"manual:{uuid4().hex}"
    )

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO referral_clients (
                platform,
                platform_user_id,
                username,
                first_name,
                ref_code,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "manual",
                manual_user_id,
                None,
                first_name.strip(),
                normalized_code,
                datetime.now().isoformat(
                    timespec="seconds"
                ),
            ),
        )

        connection.commit()

        return int(
            cursor.lastrowid
        )


# =========================================================
# ОПЛАЧЕННЫЙ ПЕРВЫЙ ВИЗИТ
# =========================================================

def mark_first_visit_paid(
    client_id: int,
    bonus_amount: int,
) -> None:

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE referral_clients
            SET
                first_visit_paid = 1,
                bonus_amount = ?,
                paid_at = ?
            WHERE id = ?
            """,
            (
                bonus_amount,
                datetime.now().isoformat(
                    timespec="seconds"
                ),
                client_id,
            ),
        )

        connection.commit()


# =========================================================
# БОНУС РЕКОМЕНДАТЕЛЮ ВЫДАН
# =========================================================

def mark_bonus_paid(
    client_id: int,
) -> None:

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE referral_clients
            SET bonus_paid = 1
            WHERE id = ?
            """,
            (
                client_id,
            ),
        )

        connection.commit()


# =========================================================
# СПИСОК РЕФЕРАЛОВ
# =========================================================

def get_referral_clients():
    with get_connection() as connection:

        return connection.execute(
            """
            SELECT
                referral_clients.*,
                referral_partners.name
                    AS referrer_name

            FROM referral_clients

            LEFT JOIN referral_partners
                ON referral_partners.code
                = referral_clients.ref_code

            ORDER BY
                referral_clients.id DESC
            """
        ).fetchall()


# =========================================================
# СТАТИСТИКА ПО КОДАМ
# =========================================================

def get_referral_summary():
    with get_connection() as connection:

        return connection.execute(
            """
            SELECT
                referral_partners.code,
                referral_partners.name,

                COUNT(
                    referral_clients.id
                ) AS clients_count,

                SUM(
                    CASE
                        WHEN referral_clients.first_visit_paid = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS paid_clients_count,

                COALESCE(
                    SUM(
                        referral_clients.bonus_amount
                    ),
                    0
                ) AS total_bonus,

                COALESCE(
                    SUM(
                        CASE
                            WHEN referral_clients.bonus_paid = 0
                            THEN referral_clients.bonus_amount
                            ELSE 0
                        END
                    ),
                    0
                ) AS bonus_to_pay

            FROM referral_partners

            LEFT JOIN referral_clients
                ON referral_clients.ref_code
                = referral_partners.code

            WHERE
                referral_partners.is_active = 1

            GROUP BY
                referral_partners.id

            ORDER BY
                referral_partners.name
            """
        ).fetchall()


# =========================================================
# ИНИЦИАЛИЗАЦИЯ
# =========================================================

init_referral_db()