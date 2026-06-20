with stg as (
    select * from {{ ref('stg_jobs') }}
),

exploded as (
    select
        id,
        posted_date,
        keyword,
        trim(unnest(skills_array)) as skill
    from stg
),

counted as (
    select
        skill,
        count(*) as job_count,
        count(distinct posted_date::date) as days_seen
    from exploded
    where skill != ''
    and skill is not null
    group by skill
)

select * from counted
order by job_count desc