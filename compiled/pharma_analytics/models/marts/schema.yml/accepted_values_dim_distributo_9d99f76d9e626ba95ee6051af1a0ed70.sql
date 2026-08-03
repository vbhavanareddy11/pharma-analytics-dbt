
    
    

with all_values as (

    select
        name_reconciliation_status as value_field,
        count(*) as n_records

    from ANALYTICS.DBT_BHAVANA.dim_distributor
    group by name_reconciliation_status

)

select *
from all_values
where value_field not in (
    'match','mismatch','missing_in_salesforce'
)


