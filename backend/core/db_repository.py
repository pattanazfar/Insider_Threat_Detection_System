from config.database import SessionLocal
from db_models.raw_logs_model import RawLogs
from db_models.clean_logs_model import CleanLogs

# ✅ EXISTING MODELS
from db_models.temporal_features_model import TemporalFeatures
from db_models.peer_features_model import PeerFeatures
from db_models.blocked_employees_model import BlockedEmployee
# ✅ FINAL MODEL
from db_models.final_features_model import FinalFeatures
from db_models.anomaly_results_model import AnomalyResults
import pandas as pd
from sqlalchemy import case, func


class DBRepository:
    # ===============================
    # RAW LOGS
    # ===============================
    def save_raw_logs(self, df):
        session = SessionLocal()

        try:
            session.query(RawLogs).delete()

            df = df.copy().fillna(0)

            records = df.to_dict(orient="records")
            session.bulk_insert_mappings(RawLogs, records)

            session.commit()

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()

    def get_raw_logs(self):
        session = SessionLocal()

        try:
            data = session.query(RawLogs).all()

            return pd.DataFrame([
                {
                    "employee": r.employee,
                    "date": r.date,
                    "logon_count": r.logon_count,
                    "file_count": r.file_count,
                    "device_count": r.device_count,
                    "email_count": r.email_count,
                    "http_count": r.http_count
                }
                for r in data
            ])

        finally:
            session.close()

    # ===============================
    # CLEAN LOGS
    # ===============================
    def save_clean_logs(self, df):
        session = SessionLocal()

        try:
            session.query(CleanLogs).delete()

            df = df.copy().fillna(0)

            records = df.to_dict(orient="records")
            session.bulk_insert_mappings(CleanLogs, records)

            session.commit()

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()

    def get_clean_logs(self):
        session = SessionLocal()

        try:
            data = session.query(CleanLogs).all()

            return pd.DataFrame([
                {
                    "employee": r.employee,
                    "date": r.date,
                    "logon_count": r.logon_count,
                    "file_count": r.file_count,
                    "device_count": r.device_count,
                    "email_count": r.email_count,
                    "http_count": r.http_count
                }
                for r in data
            ])

        finally:
            session.close()

    # ===============================
    # TEMPORAL FEATURES
    # ===============================
    def save_temporal_features(self, df):
        session = SessionLocal()

        try:
            session.query(TemporalFeatures).delete()

            df = df.copy().fillna(0)

            records = df.to_dict(orient="records")
            session.bulk_insert_mappings(TemporalFeatures, records)

            session.commit()

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()

    def get_temporal_features(self):
        session = SessionLocal()

        try:
            data = session.query(TemporalFeatures).all()

            return pd.DataFrame([
                {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
                for row in data
            ])

        finally:
            session.close()

    # ===============================
    # PEER FEATURES
    # ===============================
    def save_peer_features(self, df):
        session = SessionLocal()

        try:
            session.query(PeerFeatures).delete()

            df = df.copy().fillna(0)

            records = df.to_dict(orient="records")
            session.bulk_insert_mappings(PeerFeatures, records)

            session.commit()

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()

    def get_peer_features(self):
        session = SessionLocal()

        try:
            data = session.query(PeerFeatures).all()

            return pd.DataFrame([
                {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
                for row in data
            ])

        finally:
            session.close()

    # ===============================
    # FINAL FEATURES (FIXED 🔥🔥🔥)
    # ===============================
    def save_final_features(self, df):
        session = SessionLocal()

        try:
            session.query(FinalFeatures).delete()

            df = df.copy()
            df["date"] = pd.to_datetime(df["date"]).dt.date
            df = df.fillna(0)

            # ✅ FILTER ONLY REQUIRED COLUMNS
            allowed_cols = [
                "employee", "date",

                "logon_count", "file_count", "device_count", "email_count", "http_count",

                "total_activity",

                "logon_ratio", "file_ratio", "device_ratio", "email_ratio", "http_ratio",

                "logon_log", "file_log", "device_log", "email_log", "http_log",

                "high_file_activity", "high_http_activity",

                "behavior_deviation_score", "resource_access_score"
            ]

            df = df[allowed_cols]

            records = df.to_dict(orient="records")
            session.bulk_insert_mappings(FinalFeatures, records)

            session.commit()

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()

    def get_final_features(self):
        session = SessionLocal()

        try:
            data = session.query(FinalFeatures).all()

            df = pd.DataFrame([
                {k: v for k, v in row.__dict__.items() if not k.startswith("_")}
                for row in data
            ])

            if df.empty:
                raise ValueError("No data received from DB")

            return df

        finally:
            session.close()
    # ===============================
    # ANOMALY RESULTS (NEW ✅)
    # ===============================
    def save_anomaly_results(self, df):
        session = SessionLocal()

        try:
            # 🔹 Clear old data
            session.query(AnomalyResults).delete()

            df = df.copy()

            # 🔹 Ensure correct date format
            df["date"] = pd.to_datetime(df["date"]).dt.date

            # 🔹 Fill missing values
            df = df.fillna(0)

            # 🔹 Keep only required columns
            allowed_cols = [
                "employee",
                "date",
                "anomaly_score",
                "risk_score",   # ✅ NEW
                "is_anomaly",
                "risk_level"
            ]

            df = df[allowed_cols]

            # 🔹 Convert to records
            records = df.to_dict(orient="records")

            # 🔹 Bulk insert (FAST)
            session.bulk_insert_mappings(AnomalyResults, records)

            session.commit()

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()


    def get_anomaly_results(self):
        session = SessionLocal()

        try:
            from db_models.final_features_model import FinalFeatures
            from db_models.anomaly_results_model import AnomalyResults

            risk_priority = case(
                (
                    func.upper(func.trim(AnomalyResults.risk_level)) == "HIGH",
                    3,
                ),
                (
                    func.upper(func.trim(AnomalyResults.risk_level)) == "MEDIUM",
                    2,
                ),
                (
                    func.upper(func.trim(AnomalyResults.risk_level)) == "LOW",
                    1,
                ),
                else_=0,
            )

            ranked_results = (
                session.query(
                    AnomalyResults.employee,
                    AnomalyResults.date,
                    AnomalyResults.risk_score,
                    AnomalyResults.risk_level,
                    AnomalyResults.anomaly_score,
                    AnomalyResults.is_anomaly,

                    # 🔥 ADD FEATURES
                    FinalFeatures.file_count,
                    FinalFeatures.http_count,
                    FinalFeatures.email_count,
                    FinalFeatures.device_count,
                    FinalFeatures.logon_count,
                    FinalFeatures.total_activity,
                    func.row_number()
                    .over(
                        partition_by=AnomalyResults.employee,
                        order_by=(
                            risk_priority.desc(),
                            AnomalyResults.risk_score.desc(),
                        ),
                    )
                    .label("_row_number"),
                )
                .join(
                    FinalFeatures,
                    (AnomalyResults.employee == FinalFeatures.employee) &
                    (AnomalyResults.date == FinalFeatures.date)
                )
                .subquery()
            )

            response_columns = [
                column
                for column in ranked_results.c
                if column.name != "_row_number"
            ]
            results = (
                session.query(*response_columns)
                .filter(ranked_results.c._row_number == 1)
                .order_by(ranked_results.c.employee)
                .all()
            )

            df = pd.DataFrame([dict(row._mapping) for row in results])

            return df

        finally:
            session.close()
# ===============================
# BLOCKED EMPLOYEES ✅
# ===============================
    def block_employee(self, employee: str):
        session = SessionLocal()

        try:
            existing = session.query(BlockedEmployee).filter_by(employee=employee).first()
            if existing:
                return

            obj = BlockedEmployee(employee=employee)  # ✅ removed reason
            session.add(obj)
            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def get_blocked_employees(self):
        session = SessionLocal()

        try:
            data = session.query(BlockedEmployee).all()

            return [
                {"employee": x.employee}   # ✅ removed reason
                for x in data
            ]

        finally:
            session.close()


    def unblock_employee(self, employee: str):
        session = SessionLocal()

        try:
            session.query(BlockedEmployee).filter_by(employee=employee).delete()
            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
