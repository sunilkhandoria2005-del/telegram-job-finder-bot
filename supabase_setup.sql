-- Supabase Tables for AI Job Telegram Bot
-- Run these in your Supabase SQL Editor to enable data persistence

-- 1. Create user_profiles table
create table public.user_profiles (
    id uuid default uuid_generate_v4() primary key,
    telegram_user_id text unique not null,
    name text,
    education jsonb default '[]',
    experience jsonb default '[]',
    projects jsonb default '[]',
    target_roles jsonb default '[]',
    skills jsonb default '[]',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Create user_preferences table
create table public.user_preferences (
    id uuid default uuid_generate_v4() primary key,
    telegram_user_id text unique not null,
    location_preference text,
    work_mode_preference text,
    job_type_preference text,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable Row Level Security (RLS) if needed (optional)
alter table public.user_profiles enable row level security;
alter table public.user_preferences enable row level security;

-- Create policies for public access (adjust based on your security needs)
-- These policies allow anyone with the anon key to perform operations
-- For production, you might want to implement more restrictive policies

create policy "Public access for user_profiles"
on public.user_profiles
for all
using (true)
with check (true);

create policy "Public access for user_preferences"
on public.user_preferences
for all
using (true)
with check (true);