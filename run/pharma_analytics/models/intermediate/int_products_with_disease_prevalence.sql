
  create or replace   view ANALYTICS.DBT_BHAVANA.int_products_with_disease_prevalence
  
  
  
  
  as (
    

/*
  int_products_with_disease_prevalence
  ------------------------------------
  Cross-joins products to disease prevalence at each zone.
  For each product, produces one row per zone where its disease category
  has a prevalence score.

  Powers the launch-targeting business question:
    "For a new device targeting disease X, which zones are high-prevalence
     AND where do we currently under-index on sales?"

  Grain: one row per (product, zone).
*/

with products as (

    select
        material_id,
        material_code,
        material_name,
        product_line,
        product_family,
        therapy_area,
        business_unit,
        disease_category,
        list_price,
        is_active
    from ANALYTICS.DBT_BHAVANA.stg_sap__material_master
    where is_active = true    -- launch targeting only relevant for currently-sold products

),

prevalence as (

    select
        zone_code,
        disease_category,
        prevalence_score,
        source                  as prevalence_source,
        updated_date            as prevalence_updated_date
    from ANALYTICS.DBT_BHAVANA.region_disease_prevalence

),

zone_metadata as (

    select
        zone_code,
        sub_zone_name,
        zone_name,
        country,
        region
    from ANALYTICS.DBT_BHAVANA.zone_hierarchy

),

joined as (

    select
        -- Product keys and context
        p.material_id,
        p.material_code,
        p.material_name,
        p.product_line,
        p.product_family,
        p.therapy_area,
        p.business_unit,
        p.disease_category,
        p.list_price,

        -- Zone context
        pv.zone_code,
        z.sub_zone_name,
        z.zone_name,
        z.country,
        z.region,

        -- Prevalence signal
        pv.prevalence_score,
        pv.prevalence_source,
        pv.prevalence_updated_date,

        -- Categorize prevalence for easier filtering downstream
        case
            when pv.prevalence_score >= 0.60 then 'high'
            when pv.prevalence_score >= 0.45 then 'medium'
            else 'low'
        end as prevalence_tier

    from products p
    inner join prevalence pv
        on p.disease_category = pv.disease_category
    left join zone_metadata z
        on pv.zone_code = z.zone_code

)

select * from joined
  );

