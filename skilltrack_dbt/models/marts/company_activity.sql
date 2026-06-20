with stg as (
    select * from {{ ref('stg_jobs') }}
)

select
    company,
    count(*) as total_jobs,
    count(distinct keyword) as categories_hiring_in,
    min(posted_date::date) as first_seen,
    max(posted_date::date) as last_seen
from stg
where company != 'N/A'
group by company
order by total_jobs desc