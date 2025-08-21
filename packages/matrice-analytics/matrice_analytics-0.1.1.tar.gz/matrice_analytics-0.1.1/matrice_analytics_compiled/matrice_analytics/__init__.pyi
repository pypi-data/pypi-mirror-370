"""Auto-generated stubs for package: matrice_analytics."""
from typing import Any

from .post_processing import config, processor
from .post_processing.advanced_tracker import base, config, kalman_filter, matching, strack, tracker
from .post_processing.core import base, config, config_utils
from .post_processing.ocr import easyocr_extractor, postprocessing, preprocessing
from .post_processing.test_cases import run_tests, test_advanced_customer_service, test_basic_counting_tracking, test_comprehensive, test_config, test_customer_service, test_data_generators, test_people_counting, test_processor, test_utilities, test_utils
from .post_processing.usecases import Histopathological_Cancer_Detection_img, abandoned_object_detection, advanced_customer_service, age_detection, anti_spoofing_detection, assembly_line_detection, banana_defect_detection, basic_counting_tracking, blood_cancer_detection_img, car_damage_detection, car_part_segmentation, car_service, cardiomegaly_classification, chicken_pose_detection, child_monitoring, color_detection, color_map_utils, concrete_crack_detection, crop_weed_detection, customer_service, defect_detection_products, distracted_driver_detection, drowsy_driver_detection, emergency_vehicle_detection, face_emotion, face_recognition, fashion_detection, field_mapping, fire_detection, flare_analysis, flower_segmentation, gas_leak_detection, gender_detection, human_activity_recognition, intrusion_detection, leaf, leaf_disease, leak_detection, license_plate_detection, license_plate_monitoring, litter_monitoring, mask_detection, parking, parking_space_detection, pedestrian_detection, people_counting, pipeline_detection, plaque_segmentation_img, pothole_segmentation, ppe_compliance, price_tag_detection, proximity_detection, road_lane_detection, road_traffic_density, road_view_segmentation, shelf_inventory_detection, shoplifting_detection, shopping_cart_analysis, skin_cancer_classification_img, smoker_detection, solar_panel, template_usecase, theft_detection, traffic_sign_monitoring, underwater_pollution_detection, vehicle_monitoring, warehouse_object_segmentation, waterbody_segmentation, weapon_detection, weld_defect_detection, windmill_maintenance, wound_segmentation
from .post_processing.usecases.color import color_map_utils, color_mapper
from .post_processing.utils import advanced_counting_utils, advanced_helper_utils, advanced_tracking_utils, alerting_utils, category_mapping_utils, color_utils, counting_utils, filter_utils, format_utils, geometry_utils, smoothing_utils, tracking_utils


def __getattr__(name: str) -> Any: ...