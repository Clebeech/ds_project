import csv
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import County, CountyStatistic, Interview, Surveyor


def _to_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _to_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def _to_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"是", "true", "1", "y", "yes"}


def _to_date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _clean_payload(row: Dict[str, Any], exclude: Iterable[str]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    exclude_set = set(exclude)
    for key, value in row.items():
        if key in exclude_set:
            continue
        text = str(value).strip() if value is not None else ""
        if not text:
            payload[key] = None
            continue
        try:
            payload[key] = float(text)
        except ValueError:
            payload[key] = text
    return payload


class Command(BaseCommand):
    help = "Load processed CSV files under settings.PROCESSED_DIR into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove existing County, Surveyor and Interview data before import.",
        )

    def handle(self, *args, **options):
        processed_dir = Path(settings.PROCESSED_DIR)
        if not processed_dir.exists():
            raise CommandError(f"Processed directory not found: {processed_dir}")

        with transaction.atomic():
            if options["clear"]:
                Interview.objects.all().delete()
                Surveyor.objects.all().delete()
                CountyStatistic.objects.all().delete()
                County.objects.all().delete()
                self.stdout.write(self.style.WARNING("Existing records cleared."))

            county_count = self._load_counties(processed_dir)
            poverty_updates = self._load_poverty_flags(processed_dir)
            stats_count = self._load_statistics(processed_dir)
            surveyor_count = self._load_surveyors(processed_dir)
            interview_count = self._load_interviews(processed_dir)

        self.stdout.write(self.style.SUCCESS("Import finished."))
        self.stdout.write(
            f"Counties: {county_count} (poverty tagged: {poverty_updates}) | "
            f"Statistics: {stats_count} | Surveyors: {surveyor_count} | Interviews: {interview_count}"
        )

    def _load_counties(self, processed_dir: Path) -> int:
        path = processed_dir / "county_profile.csv"
        if not path.exists():
            raise CommandError(f"Missing county_profile.csv at {path}")
        created = 0
        seen = set()
        with path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                county_code = (row.get("CountyCode") or "").strip()
                if not county_code or county_code in seen:
                    continue
                seen.add(county_code)
                county, is_created = County.objects.update_or_create(
                    county_code=county_code,
                    defaults={
                        "name": (row.get("地区名称") or "").strip(),
                        "province": (row.get("所属省份") or "").strip(),
                        "prefecture": (row.get("所属城市") or "").strip(),
                        "longitude": _to_float(row.get("经度")),
                        "latitude": _to_float(row.get("纬度")),
                    },
                )
                if is_created:
                    created += 1
        return created

    def _load_poverty_flags(self, processed_dir: Path) -> int:
        path = processed_dir / "poverty_county_list.csv"
        if not path.exists():
            return 0
        updated = 0
        with path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                code_int = _to_int(row.get("行政区划代码"))
                if code_int is None:
                    continue
                county_code = f"{code_int:06d}"
                if not county_code:
                    continue
                try:
                    county = County.objects.get(pk=county_code)
                except County.DoesNotExist:
                    continue
                region_tag = (row.get("所属地域") or "").strip()
                county.region_tag = region_tag
                county.is_target = True
                county.save(update_fields=["region_tag", "is_target"])
                updated += 1
        return updated

    def _load_statistics(self, processed_dir: Path) -> int:
        path = processed_dir / "county_profile.csv"
        if not path.exists():
            return 0
        count = 0
        with path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                county_code = (row.get("CountyCode") or "").strip()
                year = _to_int(row.get("年份"))
                if not county_code or year is None:
                    continue
                try:
                    county = County.objects.get(pk=county_code)
                except County.DoesNotExist:
                    continue
                payload = _clean_payload(
                    row,
                    exclude=[
                        "CountyCode",
                        "年份",
                        "地区名称",
                        "经度",
                        "纬度",
                        "所属省份",
                        "所属城市",
                    ],
                )
                CountyStatistic.objects.update_or_create(
                    county=county,
                    year=year,
                    defaults={"payload": payload},
                )
                count += 1
        return count

    def _load_surveyors(self, processed_dir: Path) -> int:
        path = processed_dir / "surveyors.csv"
        if not path.exists():
            raise CommandError(f"Missing surveyors.csv at {path}")
        count = 0
        with path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                surveyor_id = (row.get("调研员ID") or "").strip()
                if not surveyor_id:
                    continue
                county_code = (row.get("负责县域ID") or "").strip()
                primary_county = None
                if county_code:
                    primary_county = County.objects.filter(pk=county_code).first()
                surveyor, _ = Surveyor.objects.update_or_create(
                    surveyor_id=surveyor_id,
                    defaults={
                        "name": (row.get("姓名") or "").strip(),
                        "gender": (row.get("性别") or "").strip(),
                        "school": (row.get("所属院系") or "").strip(),
                        "education_level": (row.get("学历") or "").strip(),
                        "major": (row.get("专业方向") or "").strip(),
                        "phone": (row.get("联系电话") or "").strip(),
                        "email": (row.get("电子邮箱") or "").strip(),
                        "team_id": (row.get("所属分队ID") or "").strip(),
                        "primary_county": primary_county,
                        "role": (row.get("调研角色") or "").strip(),
                        "batch_label": (row.get("参与调研批次") or "").strip(),
                        "start_date": _to_date(row.get("调研开始时间")),
                        "end_date": _to_date(row.get("调研结束时间")),
                        "interview_completed": _to_int(row.get("已完成访谈次数")) or 0,
                        "interview_pending": _to_int(row.get("待补访次数")) or 0,
                        "expertise": (row.get("调研专长") or "").strip(),
                        "training_completed": _to_bool(row.get("培训完成状态")),
                        "equipment_status": (row.get("设备领用状态") or "").strip(),
                        "notes": (row.get("备注") or "").strip(),
                    },
                )
                count += 1
        return count

    def _load_interviews(self, processed_dir: Path) -> int:
        path = processed_dir / "interviews.csv"
        if not path.exists():
            raise CommandError(f"Missing interviews.csv at {path}")
        count = 0
        with path.open(newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                interview_id = (row.get("访谈记录id") or "").strip()
                if not interview_id:
                    continue
                county = County.objects.filter(pk=(row.get("县id") or "").strip()).first()
                surveyor = Surveyor.objects.filter(pk=(row.get("调研人id") or "").strip()).first()
                Interview.objects.update_or_create(
                    interview_id=interview_id,
                    defaults={
                        "county": county,
                        "surveyor": surveyor,
                        "interviewee_id": (row.get("访谈对象id") or "").strip(),
                        "interviewee_name": (row.get("受访人姓名") or "").strip(),
                        "interviewee_profile": (row.get("受访人信息") or "").strip(),
                        "transcript": (row.get("访谈内容") or "").strip(),
                        "interview_date": _to_date(row.get("访谈时间")),
                        "location": (row.get("访谈地点") or "").strip(),
                        "quality_score": _to_int(row.get("访谈质量")),
                    },
                )
                count += 1
        return count

