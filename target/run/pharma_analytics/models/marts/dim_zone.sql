
  
    

create or replace transient table ANALYTICS.DBT_BHAVANA.dim_zone
    
    
    
    as (

/*
  dim_zone
  --------
  Zone dimension — geographic hierarchy plus average disease prevalence
  per zone (aggregated from the seed) for quick launch-targeting queries.
  Grain: one row per zone.
*/

with zones as (

    select * from ANALYTICS.DBT_BHAVANA.zone_hierarchy

),

prevalence_summary as (

    -- Aggregate: how many disease categories does this zone have data for,
    -- what's the average prevalence, and what's the max prevalence category?
    select
        zone_code,
        count(distinct disease_category)    as diseases_measured,
        round(avg(prevalence_score), 3)     as avg_prevalence_score,
        max(prevalence_score)               as max_prevalence_score
    from ANALYTICS.DBT_BHAVANA.region_disease_prevalence
    group by zone_code

),

final as (

    select
        -- Surrogate key
        md5(z.zone_code)             as zone_sk,

        -- Natural key
        z.zone_code                  as zone_nk,

        -- Hierarchy
        z.sub_zone_name,
        z.zone_name,
        z.country,
        z.region,

        -- Aggregated prevalence context (per zone)
        coalesce(p.diseases_measured, 0)     as diseases_measured,
        p.avg_prevalence_score,
        p.max_prevalence_score

    from zones z
    left join prevalence_summary p
        on z.zone_code = p.zone_code

)

select * from final
    )
;


  