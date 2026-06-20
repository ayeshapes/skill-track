with source as (
    select * from public.jobs
),

cleaned as (
    select
        id,
        trim(title) as title,
        trim(company) as company,
        trim(location) as location,
        trim(experience) as experience,
        trim(salary) as salary,
        posted_date,
        keyword,
        job_url,
        scraped_at,
        -- split skills string into array
        string_to_array(skills, ',') as skills_array
    from source
    where title is not null
    and title != 'N/A'
)

select * from cleaned