

/*
  dim_date
  --------
  Date dimension covering 2020-01-01 through 2028-12-31.
  Standard analytics dim — every fact date joins here for time-based
  attributes (year, quarter, month, weekday, fiscal quarter, etc.).
  Grain: one row per calendar date.
*/

with date_spine as (

    -- Generate every date between the bounds using Snowflake's row generator
    select
        dateadd(day, seq4(), '2020-01-01'::date) as calendar_date
    from table(generator(rowcount => 3287))       -- ~9 years of dates

),

final as (

    select
        -- Surrogate + natural key (date is its own key)
        calendar_date,
        to_char(calendar_date, 'YYYY-MM-DD')          as date_id,

        -- Standard parts
        year(calendar_date)                            as year,
        quarter(calendar_date)                         as quarter,
        month(calendar_date)                           as month,
        day(calendar_date)                             as day_of_month,
        dayofweek(calendar_date)                       as day_of_week,
        weekofyear(calendar_date)                      as week_of_year,
        dayofyear(calendar_date)                       as day_of_year,

        -- Labels
        monthname(calendar_date)                       as month_name,
        dayname(calendar_date)                         as day_name,
        year(calendar_date) || '-Q' || quarter(calendar_date)  as year_quarter,
        to_char(calendar_date, 'YYYY-MM')              as year_month,

        -- Flags
        case when dayofweek(calendar_date) in (0, 6) then true else false end  as is_weekend,
        case when day(calendar_date) = 1 then true else false end              as is_month_start,
        case when calendar_date = last_day(calendar_date) then true else false end as is_month_end

    from date_spine
    where calendar_date <= '2028-12-31'::date

)

select * from final