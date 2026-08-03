

with source as (

    select * from RAW.SALESFORCE.account

),

renamed as (

    select
        -- Keys
        id                     as account_id,
        account_number,
        parent_id              as parent_account_id,

        -- Descriptive
        name                   as account_name,
        account_type,
        tier,
        country,
        zone,
        city,
        billing_address,

        -- Distributor overlap flag
        is_distributor,

        -- Contact info
        primary_contact_name,
        primary_contact_email,
        primary_contact_phone,

        -- Ownership + terms
        assigned_sales_rep_id,
        contract_start_date,
        payment_terms,

        -- Lifecycle
        is_active,
        is_deleted,

        -- Metadata
        created_date           as created_at,
        last_modified_date     as updated_at

    from source
    where is_deleted = false

)

select * from renamed