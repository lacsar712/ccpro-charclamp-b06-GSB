from __future__ import annotations

from datetime import timedelta

from charclamp.domain.models import BurnShift, Clamp, Site, User, utcnow
from charclamp.infra.db import SyncSessionLocal
from charclamp.infra.security import hash_password


def seed_demo() -> None:
    with SyncSessionLocal() as session:
        admin = session.query(User).filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", role="admin", password_hash=hash_password("123456"))
            session.add(admin)
        else:
            admin.password_hash = hash_password("123456")
            admin.role = "admin"

        worker = session.query(User).filter_by(username="worker").first()
        if not worker:
            worker = User(username="worker", role="worker", password_hash=hash_password("123456"))
            session.add(worker)
        else:
            worker.password_hash = hash_password("123456")
            worker.role = "worker"

        if session.query(Site).first():
            session.commit()
            return

        site = Site(name="乌石岗焖烧坞", location="河谷台地北侧", notes="青冈为主，夜班闷窑")
        session.add(site)
        session.flush()

        c1 = Clamp(site=site, code="坞东-甲", status=Clamp.STATUS_BURNING, wood_species="青冈")
        c2 = Clamp(site=site, code="坞东-乙", status=Clamp.STATUS_STACKED, wood_species="松木")
        c3 = Clamp(site=site, code="河沿-丙", status=Clamp.STATUS_DRAWN, wood_species="栎木")
        session.add_all([c1, c2, c3])
        session.flush()

        now = utcnow()
        # 每座窑都至少有一条班次，且分布在多个自然日，便于演示时间轴日折叠。
        session.add_all(
            [
                BurnShift(
                    clamp=c1,
                    started_at=now - timedelta(hours=2),
                    peak_temp_c=None,
                    charcoal_grade="B",
                    notes="本班在岗，峰值待测",
                ),
                BurnShift(
                    clamp=c1,
                    started_at=now - timedelta(hours=9),
                    peak_temp_c=448.0,
                    charcoal_grade="A",
                    notes="夜班焖烧，温度平稳",
                ),
                BurnShift(
                    clamp=c1,
                    started_at=now - timedelta(days=1, hours=4),
                    peak_temp_c=455.0,
                    charcoal_grade="A",
                    notes="峰值已过，可出炭",
                ),
                BurnShift(
                    clamp=c2,
                    started_at=now - timedelta(hours=5),
                    peak_temp_c=None,
                    charcoal_grade="B",
                    notes="刚点火，未测峰值",
                ),
                BurnShift(
                    clamp=c2,
                    started_at=now - timedelta(days=1, hours=6),
                    peak_temp_c=410.0,
                    charcoal_grade="B",
                    notes="松木试烧班",
                ),
                BurnShift(
                    clamp=c3,
                    started_at=now - timedelta(days=2),
                    peak_temp_c=520.0,
                    charcoal_grade="A+",
                    notes="已出炭班次",
                ),
                BurnShift(
                    clamp=c3,
                    started_at=now - timedelta(days=3, hours=7),
                    peak_temp_c=505.0,
                    charcoal_grade="A",
                    notes="栎木大班",
                ),
                BurnShift(
                    clamp=c3,
                    started_at=now - timedelta(days=5),
                    peak_temp_c=498.0,
                    charcoal_grade="A",
                    notes="月初焖烧",
                ),
            ]
        )
        session.commit()
