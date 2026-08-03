
    
    

select
    sales_rep_nk as unique_field,
    count(*) as n_records

from ANALYTICS.DBT_BHAVANA.dim_sales_rep
where sales_rep_nk is not null
group by sales_rep_nk
having count(*) > 1


