# import typing as t

from kedro.pipeline import node
from kedro.pipeline.node import Node

from .dataloading_nodes import (
    check_data_inputs,
    node_write_categories,
    node_write_company,
    node_write_datapoints,
    node_write_flags,
    node_write_product_categories,
    node_write_product_data,
    node_write_products,
    node_write_sku_data,
    node_write_skus,
    node_write_store_data,
    node_write_stores,
    node_write_time_product_data,
    node_write_time_region_data,
    node_write_time_sku_data,
    node_write_time_store_data,
)

# node_write_categories,; node_write_datapoints,; node_write_flags,; node_write_product_categories,; node_write_product_data,; node_write_products,; node_write_sku_data,; node_write_skus,; node_write_store_data,; node_write_stores,; node_write_time_product_data,; node_write_time_region_data,; node_write_time_sku_data,; node_write_time_store_data,


def create_writing_sub_pipeline() -> list[Node]:
    sub_pipeline = [
        #################################### Data input validation ########################################
        node(
            func=check_data_inputs,
            inputs=[
                "params:company_name",
                "params:dataset_type",
                "min_date",
                "max_date",
                "frequency",
                "store_region_map",
                "categories_dict",
                "categories_level_description",
                "products",
                "time_sku_data",
                "time_sku_feature_description_map",
                "flags",
                "store_feature_description_map",
                "store_feature_map",
                "product_feature_description_map",
                "product_feature_map",
                "sku_feature_description_map",
                "sku_feature_map",
                "time_product_feature_description_map",
                "time_product_feature_map",
                "time_region_feature_description_map",
                "time_region_feature_map",
                "time_store_feature_description_map",
                "time_store_feature_map",
            ],
            outputs="check_passed",
            name="check_data_inputs",
        ),
        #################################### Write mandatory data #######################################
        node(
            func=node_write_company,
            inputs={
                "data_loader": "data_loader",
                "company_name": "params:company_name",
                "dataset_type": "params:dataset_type",
                "description": "params:description",
                "min_date": "min_date",
                "max_date": "max_date",
                "frequency": "frequency",
                "check_passed": "check_passed",
            },
            outputs="company_id",
            name="write_company",
        ),
        node(
            func=node_write_stores,
            inputs={
                "data_loader": "data_loader",
                "store_region_map": "store_region_map",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="store_ids",
            name="write_stores",
        ),
        node(
            func=node_write_categories,
            inputs={
                "data_loader": "data_loader",
                "categories_dict": "categories_dict",
                "level_names": "categories_level_description",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="category_ids",
            name="write_categories",
        ),
        node(
            func=node_write_products,
            inputs={
                "data_loader": "data_loader",
                "products": "products",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="product_ids",
            name="write_products",
        ),
        node(
            func=node_write_product_categories,
            inputs={
                "data_loader": "data_loader",
                "products": "products",
                "category_ids": "category_ids",
                "product_ids": "product_ids",
                "check_passed": "check_passed",
            },
            outputs="write_product_categories_done",
            name="write_product_categories",
        ),
        node(
            func=node_write_skus,
            inputs={
                "data_loader": "data_loader",
                "time_sku_data": "time_sku_data",
                "store_ids": "store_ids",
                "product_ids": "product_ids",
                "check_passed": "check_passed",
            },
            outputs="sku_ids",
            name="write_skus",
        ),
        node(
            func=node_write_datapoints,
            inputs={
                "data_loader": "data_loader",
                "time_sku_data": "time_sku_data",
                "sku_ids": "sku_ids",
                "check_passed": "check_passed",
            },
            outputs="datapoint_ids",
            name="write_datapoints",
        ),
        node(
            func=node_write_time_sku_data,
            inputs={
                "data_loader": "data_loader",
                "time_sku_feature_description_map": "time_sku_feature_description_map",
                "time_sku_data": "time_sku_data",
                "datapoint_ids": "datapoint_ids",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="time_sku_data_written",
            name="write_time_sku_data",
        ),
        node(
            func=node_write_flags,
            inputs={
                "data_loader": "data_loader",
                "flags": "flags",
                "datapoint_ids": "datapoint_ids",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="flags_written",
            name="write_flags",
        ),
        #################################### Write optional data ########################################
        node(
            func=node_write_store_data,
            inputs={
                "data_loader": "data_loader",
                "store_feature_description_map": "store_feature_description_map",
                "store_feature_map": "store_feature_map",
                "store_ids": "store_ids",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="store_features_written",
            name="write_store_data",
        ),
        node(
            func=node_write_product_data,
            inputs={
                "data_loader": "data_loader",
                "product_feature_description_map": "product_feature_description_map",
                "product_feature_map": "product_feature_map",
                "product_ids": "product_ids",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="product_features_written",
            name="write_product_data",
        ),
        node(
            func=node_write_sku_data,
            inputs={
                "data_loader": "data_loader",
                "sku_feature_description_map": "sku_feature_description_map",
                "sku_feature_map": "sku_feature_map",
                "sku_ids": "sku_ids",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="sku_features_written",
            name="write_sku_data",
        ),
        node(
            func=node_write_time_product_data,
            inputs={
                "data_loader": "data_loader",
                "time_product_feature_description_map": "time_product_feature_description_map",
                "time_product_feature_map": "time_product_feature_map",
                "product_ids": "product_ids",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="time_product_features_written",
            name="write_time_product_data",
        ),
        node(
            func=node_write_time_store_data,
            inputs={
                "data_loader": "data_loader",
                "time_store_feature_description_map": "time_store_feature_description_map",
                "time_store_feature_map": "time_store_feature_map",
                "store_ids": "store_ids",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="time_store_features_written",
            name="write_time_store_data",
        ),
        node(
            func=node_write_time_region_data,
            inputs={
                "data_loader": "data_loader",
                "time_region_feature_description_map": "time_region_feature_description_map",
                "time_region_feature_map": "time_region_feature_map",
                "company_id": "company_id",
                "check_passed": "check_passed",
            },
            outputs="time_region_features_written",
            name="write_time_region_data",
        ),
    ]

    return sub_pipeline
