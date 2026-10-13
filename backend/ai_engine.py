import logging
import os

import httpx

logger = logging.getLogger(__name__)

# Demonstration assumptions only. These are not live market quotes or official zoning data.
REGIONAL_DATA = {
    "istanbul": {
        "kadikoy": {"m2_insaat_maliyeti": 25000, "m2_satis_fiyati": 120000, "emsal": 2.07},
        "besiktas": {"m2_insaat_maliyeti": 30000, "m2_satis_fiyati": 180000, "emsal": 2.5},
        "esenyurt": {"m2_insaat_maliyeti": 12000, "m2_satis_fiyati": 25000, "emsal": 1.5},
        "default": {"m2_insaat_maliyeti": 18000, "m2_satis_fiyati": 45000, "emsal": 1.5},
    },
    "ankara": {
        "cankaya": {"m2_insaat_maliyeti": 18000, "m2_satis_fiyati": 50000, "emsal": 1.8},
        "eryaman": {"m2_insaat_maliyeti": 14000, "m2_satis_fiyati": 25000, "emsal": 1.2},
        "default": {"m2_insaat_maliyeti": 15000, "m2_satis_fiyati": 30000, "emsal": 1.5},
    },
    "izmir": {
        "karsiyaka": {"m2_insaat_maliyeti": 17000, "m2_satis_fiyati": 60000, "emsal": 1.6},
        "default": {"m2_insaat_maliyeti": 16000, "m2_satis_fiyati": 40000, "emsal": 1.4},
    },
    "default": {"m2_insaat_maliyeti": 14000, "m2_satis_fiyati": 28000, "emsal": 1.2},
}


async def fetch_geodata_from_api(location_query: str):
    """Geocode a location using Nominatim. Geocoding does not verify zoning rights."""
    user_agent = os.getenv("NOMINATIM_USER_AGENT", "").strip()
    if not user_agent:
        logger.info("NOMINATIM_USER_AGENT ayarlanmamış; geocoding atlandı.")
        return None
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(8.0, connect=3.0)) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": location_query, "format": "jsonv2", "limit": 1},
                headers={"User-Agent": user_agent},
            )
            response.raise_for_status()
            data = response.json()
            if data:
                place = data[0]
                return {
                    "display_name": place.get("display_name"),
                    "lat": place.get("lat"),
                    "lon": place.get("lon"),
                    "type": place.get("type"),
                }
    except (httpx.HTTPError, ValueError, KeyError):
        logger.exception("Geocoding başarısız")
    return None


def get_regional_data(location_str: str):
    loc = location_str.casefold()
    for city, districts in REGIONAL_DATA.items():
        if city != "default" and city in loc:
            for district, data in districts.items():
                if district != "default" and district in loc:
                    return dict(data)
            return dict(districts["default"])
    return dict(REGIONAL_DATA["default"])


async def analyze_land(image_path: str, location: str, area_sqm: float):
    # The image is validated and temporarily stored, but no vision model or parcel
    # boundary measurement is integrated yet. Do not represent it as image analysis.
    if not os.path.isfile(image_path):
        raise ValueError("Görsel dosyası bulunamadı.")
    if area_sqm <= 0:
        raise ValueError("Arsa alanı pozitif olmalıdır.")

    geo_data = await fetch_geodata_from_api(location)
    region_info = get_regional_data(location)
    emsal = region_info["emsal"]
    taks = 0.40  # Default assumption, not parcel-specific planning data.
    base_area = area_sqm * taks
    total_construction_area = area_sqm * emsal
    estimated_units = int(total_construction_area / 100)
    estimated_floors = max(1, int(total_construction_area / base_area)) if base_area else 1
    construction_cost = total_construction_area * region_info["m2_insaat_maliyeti"]
    sales_revenue = total_construction_area * region_info["m2_satis_fiyati"]

    zoning_info = {
        "emsal": emsal,
        "taks": taks,
        "max_kat": estimated_floors,  # Legacy UI/PDF field; clearly labelled as an estimate.
        "estimated_floors_from_area_ratio": estimated_floors,
        "note": "Kat sayısı yalnızca alan oranı varsayımıdır; yükseklik/plan notu kontrolü değildir.",
    }
    capacity = {
        "taban_alani_m2": round(base_area, 2),
        "toplam_insaat_alani_m2": round(total_construction_area, 2),
        "tahmini_daire_sayisi": estimated_units,  # Legacy UI/PDF compatibility.
        "tahmini_daire_sayisi_100m2": estimated_units,
    }
    return {
        "location": geo_data.get("display_name", location) if geo_data else location,
        "coordinates": {"lat": geo_data.get("lat"), "lon": geo_data.get("lon")} if geo_data else None,
        "geocoding_status": "verified_location_only" if geo_data else "not_verified",
        "api_status": "OpenStreetMap ile konum eşleştirildi; imar verisi doğrulanmadı." if geo_data
            else "Konum doğrulanamadı; varsayılan bölgesel varsayımlar kullanıldı.",
        "image_analysis_status": "not_performed",
        "assumptions": {
            "source": "built_in_demo_table",
            "taks_assumption": taks,
            "cost_and_sale_values_are_live": False,
            "zoning_values_are_official": False,
            "currency": "TRY",
        },
        "area_sqm": area_sqm,
        "zoning_info": zoning_info,
        "capacity": capacity,
        "financials": {
            "toplam_maliyet_tl": round(construction_cost, 2),
            "toplam_gelir_tl": round(sales_revenue, 2),
            "tahmini_kar_tl": round(sales_revenue - construction_cost, 2),
        },
        "concepts": [
            "Standart konut projesi — taslak fikir, mevzuat kontrolü gerekir",
            "Ticari zeminli karma proje — taslak fikir, kullanım izni kontrolü gerekir",
            "Alternatif daire büyüklükleri — mimari ve yangın/otopark koşulları kontrol edilmelidir",
        ],
    }
