with stg as (
    select * from {{ ref('stg_jobs') }}
),

parsed as (
    select
        title,
        company,
        location,
        experience,
        salary,
        posted_date
    from stg
    where salary != 'N/A'
    and salary is not null
    and salary != ''
)

select
    title,
    location,
    experience,
    count(*) as job_count,
    array_agg(distinct salary) as salary_ranges
from parsed
group by title, location, experience
order by job_count desc