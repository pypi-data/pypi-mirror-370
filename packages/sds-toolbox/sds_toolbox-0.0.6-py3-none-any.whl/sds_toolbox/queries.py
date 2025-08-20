from sds_toolbox.common import lst_of_int, lst_to_str, filter_by_date
from sqlalchemy import text

def get_jpp_type(inclure_citations = True, inclure_retweets = True, inclure_comments = True):
    join_post_post_type = ['original']
    if inclure_citations:
        join_post_post_type.append('quote')
    if inclure_retweets:
        join_post_post_type.append('share')
    if inclure_comments:
        join_post_post_type.append('comment')
    return join_post_post_type
  

def q_projects_and_importations():
    """
    Informations générales à propos des projets et des importations
    """
    _SQL = text(
    f"""select *
        from v_importations 
    """
    )
    return _SQL

def q_posts_type(importation_id, start_date, end_date):
    """
    Requête permettant de récupérer le nombre de posts par type
    """

    _SQL = """
        SELECT 
            p.type, 
            p.is_deduced,
            count(distinct p.id) as posts
        FROM posts p
        WHERE 
            p.importation_id IN ({importations})
            {filter_by_date}
        GROUP BY p.type, p.is_deduced;"""
    
    _SQL = _SQL.format(
            importations= lst_of_int(importation_id),
            filter_by_date = filter_by_date("p.created_at", start_date, end_date),
        )
    return text(_SQL)    

def q_join_post_post_type(importation_id, start_date, end_date):
    """
    Requête permettant de compter le nombre de posts par type de join_post_post 
    """

    _SQL = """
        SELECT 
            v.post_importation_id,
            v.join_post_post_type as type,
            count(distinct v.post_id) as posts
        FROM v_posts_and_quotes_forwards v
        WHERE 
            v.post_importation_id IN ({importations})
            {filter_by_date}
        GROUP BY v.join_post_post_type, v.post_importation_id
            ;"""

    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date)
    )
    return text(_SQL)

def q_distinct_posts_wt_authors_documents_text(importation_id, start_date, end_date, inclure_citations, inclure_retweets, inclure_comments):
    """
    Requête permettant de récupérer les posts distincts, avec les informations sur les auteurs et les documents associés
    """

    # On prépare les filtres de sélection de posts / commentaires / retweets / citations
    jpp_type = get_jpp_type(inclure_citations, inclure_retweets, inclure_comments)

    _SQL = """
        SELECT 
            v.post_importation_id,
            v.post_platform,
            v.post_id, 
            v.post_type,
            v.post_pf_post_id as pf_post_id,
            v.post_created_at, 
            v.post_is_deduced,
            v.post_lang,
            v.post_url,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name AS screen_name,
            v.account_description AS description,
            v.account_lang,
            v.account_url,
            v.document_id,
            v.document_text,
            v.document_text_fr,
            v.document_text_en,
            v.document_lang,
            MAX(v.account_registered_at) AS account_registered_at,
            MAX(v.account_profile_picture) AS account_profile_picture,
            MAX(v.account_followers) AS account_followers,
            MAX(v.account_following) AS account_following,
            MAX(v.account_posts) AS account_posts,
            MAX(v.account_views) AS account_views,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_engagements ELSE 0 END) AS engagements,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_reactions ELSE 0 END) AS reactions,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_comments ELSE 0 END) AS comments,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_shares ELSE 0 END) AS shares,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_views ELSE 0 END) AS views,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_quotes ELSE 0 END) AS quotes,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN 1 ELSE 0 END) as citations,
            SUM(CASE WHEN v.join_post_post_type = 'share' THEN 1 ELSE 0 END) as repartages
        FROM v_posts_and_quotes_forwards_wt_texts_and_authors v
        WHERE 
            v.post_importation_id IN ({importations})
            and v.join_post_post_type IN ({filter_jpp_type})
            {filter_by_date}
        GROUP BY 
            v.post_importation_id,
            v.post_platform,
            v.post_id, 
            v.post_pf_post_id,
            v.post_type,
            v.post_created_at, 
            v.post_is_deduced,
            v.post_lang,
            v.post_url,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name,
            v.account_description,
            v.account_lang,
            v.account_url,
            v.document_id,
            v.document_text,
            v.document_text_fr,
            v.document_text_en,
            v.document_lang
            ;"""

    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_jpp_type = lst_to_str(jpp_type),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date)
    )
    return text(_SQL)

def q_posts_wt_authors_documents_text(importation_id, start_date, end_date, inclure_citations, inclure_retweets, inclure_comments):
    """
    Requête permettant de récupérer les posts distincts, avec les informations sur les auteurs et les documents associés
    """

    # On prépare les filtres de sélection de posts / commentaires / retweets / citations
    jpp_type = get_jpp_type(inclure_citations, inclure_retweets, inclure_comments)

    _SQL = """
        SELECT 
            v.source_date,
            v.source_post_id,
            v.source_post_pf_post_id as source_pf_post_id,
            v.join_post_post_type,
            v.post_importation_id,
            v.post_platform,
            v.post_id, 
            v.post_type,
            v.post_pf_post_id as pf_post_id,
            v.post_created_at, 
            v.post_is_deduced,
            v.post_lang,
            v.post_url,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name AS screen_name,
            v.account_description AS description,
            v.account_lang,
            v.account_url,
            v.document_id,
            v.document_text,
            v.document_text_fr,
            v.document_text_en,
            v.document_lang,
            v.account_registered_at AS account_registered_at,
            v.account_profile_picture AS account_profile_picture,
            v.account_followers AS account_followers,
            v.account_following AS account_following,
            v.account_posts AS account_posts,
            v.account_views AS account_views,
            CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_engagements ELSE 0 END AS engagements,
            CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_reactions ELSE 0 END AS reactions,
            CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_comments ELSE 0 END AS comments,
            CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_shares ELSE 0 END AS shares,
            CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_views ELSE 0 END AS views,
            CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_quotes ELSE 0 END AS quotes
        FROM v_posts_and_quotes_forwards_wt_texts_and_authors v
        WHERE 
            v.post_importation_id IN ({importations})
            and v.join_post_post_type IN ({filter_jpp_type})
            {filter_by_date}
            ;"""

    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_jpp_type = lst_to_str(jpp_type),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date)
    )
    return text(_SQL)


    
def q_distinct_quotes_wt_authors_documents_text(importation_id, reprise_start_date, reprise_end_date, citation_start_date, citation_end_date):
    """
    Requête permettant de récupérer les posts distincts, avec les informations sur les auteurs et les documents associés
    """

    _SQL = """
        SELECT 
            v.post_importation_id,
            v.post_platform,
            v.post_id, 
            v.post_type,
            v.post_pf_post_id as pf_post_id,
            v.post_created_at, 
            v.post_is_deduced,
            v.post_lang,
            v.post_url,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name AS screen_name,
            v.account_description AS description,
            v.account_lang,
            v.account_url,
            v.document_id,
            v.document_text,
            v.document_text_fr,
            v.document_text_en,
            v.document_lang,
            MAX(v.account_registered_at) AS account_registered_at,
            MAX(v.account_profile_picture) AS account_profile_picture,
            MAX(v.account_followers) AS account_followers,
            MAX(v.account_following) AS account_following,
            MAX(v.account_posts) AS account_posts,
            MAX(v.account_views) AS account_views,
            MAX(v.post_engagements) AS engagements,
            MAX(v.post_reactions) AS reactions,
            MAX(v.post_comments) AS comments,
            MAX(v.post_shares) AS shares,
            MAX(v.post_views) AS views,
            MAX(v.post_quotes) AS quotes,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN 1 ELSE 0 END) as citations,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_engagements ELSE 0 END) as engagement_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_reactions ELSE 0 END) as reactions_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_comments ELSE 0 END) as commentaires_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_shares ELSE 0 END) as partages_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_quotes ELSE 0 END) as quotes_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_views ELSE 0 END) as views_des_reprises
        FROM v_posts_and_quotes_forwards_wt_texts_and_authors v
        WHERE 
            v.post_importation_id IN ({importations})
            and v.join_post_post_type ='quote'
            {filter_by_date_1}
            {filter_by_date_2}
        GROUP BY 
            v.post_importation_id,
            v.post_platform,
            v.post_id, 
            v.post_pf_post_id,
            v.post_type,
            v.post_created_at, 
            v.post_is_deduced,
            v.post_lang,
            v.post_url,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name,
            v.account_description,
            v.account_lang,
            v.account_url,
            v.document_id,
            v.document_text,
            v.document_text_fr,
            v.document_text_en,
            v.document_lang
        ORDER BY citations DESC
            ;"""
    
    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_by_date_1 = filter_by_date("v.source_date", reprise_start_date , reprise_end_date),
        filter_by_date_2 = filter_by_date("v.post_created_at", citation_start_date, citation_end_date)
    )
    return text(_SQL)

def q_distinct_shares_wt_authors_documents_text(importation_id, reprise_start_date, reprise_end_date, start_date, end_date):
    """
    Requête permettant de récupérer les posts distincts, avec les informations sur les auteurs et les documents associés
    """

    _SQL = """
        SELECT 
            v.post_importation_id,
            v.post_platform,
            v.post_id, 
            v.post_type,
            v.post_pf_post_id as pf_post_id,
            v.post_created_at, 
            v.post_is_deduced,
            v.post_lang,
            v.post_url,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name AS screen_name,
            v.account_description AS description,
            v.account_lang,
            v.account_url,
            v.document_id,
            v.document_text,
            v.document_text_fr,
            v.document_text_en,
            v.document_lang,
            MAX(v.account_registered_at) AS account_registered_at,
            MAX(v.account_profile_picture) AS account_profile_picture,
            MAX(v.account_followers) AS account_followers,
            MAX(v.account_following) AS account_following,
            MAX(v.account_posts) AS account_posts,
            MAX(v.account_views) AS account_views,
            MAX(v.post_engagements) AS engagements,
            MAX(v.post_reactions) AS reactions,
            MAX(v.post_comments) AS comments,
            MAX(v.post_shares) AS shares,
            MAX(v.post_views) AS views,
            MAX(v.post_quotes) AS quotes,
            SUM(CASE WHEN v.join_post_post_type = 'share' THEN 1 ELSE 0 END) as repartages
        FROM v_posts_and_quotes_forwards_wt_texts_and_authors v
        WHERE 
            v.post_importation_id IN ({importations})
            and v.join_post_post_type ='share'
            {filter_by_date_1}
            {filter_by_date_2}
        GROUP BY 
            v.post_importation_id,
            v.post_platform,
            v.post_id, 
            v.post_pf_post_id,
            v.post_type,
            v.post_created_at, 
            v.post_is_deduced,
            v.post_lang,
            v.post_url,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name,
            v.account_description,
            v.account_lang,
            v.account_url,
            v.document_id,
            v.document_text,
            v.document_text_fr,
            v.document_text_en,
            v.document_lang
        ORDER BY repartages DESC
            ;"""
    
    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_by_date_1 = filter_by_date("v.source_date", reprise_start_date , reprise_end_date),
        filter_by_date_2 = filter_by_date("v.post_created_at", start_date, end_date)
    )
    return text(_SQL)

def q_posts_agg_by_date(importation_id, start_date, end_date, inclure_citations, inclure_retweets, inclure_comments):
    """
    Agrège les posts par date 
    """

    # On prépare les filtres de sélection de posts / commentaires / retweets / citations
    jpp_type = get_jpp_type(inclure_citations, inclure_retweets, inclure_comments)

    _SQL = """
        WITH all_posts as (
            SELECT 
                v.post_created_at,
                v.post_importation_id,
                v.post_id, 
                v.account_id as account_id,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_engagements ELSE 0 END) AS post_engagements,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_reactions ELSE 0 END) AS post_reactions,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_comments ELSE 0 END) AS post_comments,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_shares ELSE 0 END) AS post_shares,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_views ELSE 0 END) AS post_views,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_quotes ELSE 0 END) AS post_quotes,
                SUM(CASE WHEN v.join_post_post_type = 'quote' THEN 1 ELSE 0 END) as citations,
                SUM(CASE WHEN v.join_post_post_type = 'forward' THEN 1 ELSE 0 END) as repartages
            FROM v_posts_and_quotes_forwards_wt_texts_and_authors v
            WHERE 
                v.post_importation_id IN ({importations})
                and v.join_post_post_type IN ({filter_jpp_type})
                {filter_by_date}
            GROUP BY v.post_id, v.account_id, v.post_importation_id, v.post_created_at
        )
        select 
            DATE(ap.post_created_at) as date,
            ap.post_importation_id as importation,
            count(distinct ap.post_id) as posts,
            count(distinct ap.account_id) as accounts,
            sum(ap.post_engagements) as engagements,
            sum(ap.post_views) as views,
            sum(ap.post_reactions) as reactions,
            sum(ap.post_shares) as shares,
            sum(ap.post_comments) as comments,
            sum(ap.post_quotes) as quotes,
            SUM(ap.citations) as citations,
            SUM(ap.repartages) as repartages
        from all_posts ap
        GROUP BY DATE(ap.post_created_at), ap.post_importation_id
        ORDER by DATE(ap.post_created_at) DESC;
        """
    
    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_jpp_type = lst_to_str(jpp_type),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date)
    )

    return text(_SQL)

def top_urls(importation_id, start_date, end_date, inclure_citations, inclure_retweets, inclure_comments):
    """
    Requête permettant de lister les URLs
    """

    join_post_post_type = get_jpp_type(inclure_citations, inclure_retweets, inclure_comments)


    _SQL = """
    WITH urls AS (
        SELECT 
            v.document_url as url,
            v.post_id,
            v.account_id,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_engagements ELSE 0 END) AS post_engagements,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_reactions ELSE 0 END) AS post_reactions,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_comments ELSE 0 END) AS post_comments,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_shares ELSE 0 END) AS post_shares,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_views ELSE 0 END) AS post_views,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_quotes ELSE 0 END) AS post_quotes,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN 1 ELSE 0 END) as citations,
            SUM(CASE WHEN v.join_post_post_type = 'share' THEN 1 ELSE 0 END) as repartages
        FROM v_posts_and_quotes_forwards_wt_texts_urls_and_authors v
        WHERE
            v.post_importation_id IN ({importation_id})
            and v.join_post_post_type IN ({filter_jpp_type})
            and v.document_url IS NOT NULL
            {filter_by_date}
        GROUP BY post_id, account_id, document_url
        )
        SELECT 
            u.url,
            SUM(u.citations) as citations,
            SUM(u.repartages) as repartages,
            COUNT(DISTINCT u.post_id) AS verbatims,
            COUNT(DISTINCT u.account_id) AS users,
            SUM(u.post_engagements) AS engagements,
            SUM(u.post_views) AS views,
            SUM(u.post_reactions) AS reactions,
            SUM(u.post_shares) AS shares,
            SUM(u.post_comments) AS comments,
            SUM(u.post_quotes) AS quotes
        FROM urls u
        GROUP BY u.url
        ORDER BY verbatims DESC;
     """

    _SQL = _SQL.format(
        importation_id=lst_of_int(importation_id),
        filter_jpp_type = lst_to_str(join_post_post_type),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date)
    )
    return text(_SQL)

def top_domains(importation_id, start_date, end_date, inclure_citations, inclure_retweets, inclure_comments):
    """
    Requête permettant de lister les noms de domaines
    """

    join_post_post_type = get_jpp_type(inclure_citations, inclure_retweets, inclure_comments)


    _SQL = """
    WITH urls AS (
        SELECT 
            v.document_domain as domain,
            v.document_url as url,
            v.post_id,
            v.account_id,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_engagements ELSE 0 END) AS post_engagements,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_reactions ELSE 0 END) AS post_reactions,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_comments ELSE 0 END) AS post_comments,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_shares ELSE 0 END) AS post_shares,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_views ELSE 0 END) AS post_views,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_quotes ELSE 0 END) AS post_quotes,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN 1 ELSE 0 END) as citations,
            SUM(CASE WHEN v.join_post_post_type = 'share' THEN 1 ELSE 0 END) as repartages
        FROM v_posts_and_quotes_forwards_wt_texts_urls_and_authors v
        WHERE
            v.post_importation_id IN ({importation_id})
            and v.join_post_post_type IN ({filter_jpp_type})
            and v.document_url IS NOT NULL
            {filter_by_date}
        GROUP BY v.post_id, v.account_id, v.document_domain, v.document_url
        )
        SELECT 
            u.domain,
            COUNT(DISTINCT u.url) as urls,
            SUM(u.citations) as citations,
            SUM(u.repartages) as repartages,
            COUNT(DISTINCT u.post_id) AS verbatims,
            COUNT(DISTINCT u.account_id) AS users,
            SUM(u.post_engagements) AS engagements,
            SUM(u.post_views) AS views,
            SUM(u.post_reactions) AS reactions,
            SUM(u.post_shares) AS shares,
            SUM(u.post_comments) AS comments,
            SUM(u.post_quotes) AS quotes
        FROM urls u
        GROUP BY u.domain
        ORDER BY verbatims DESC;
     """

    _SQL = _SQL.format(
        importation_id=lst_of_int(importation_id),
        filter_jpp_type = lst_to_str(join_post_post_type),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date)
    )
    return text(_SQL)

def top_hashtags(importation_id, start_date, end_date, inclure_citations, inclure_retweets, inclure_comments):
    """
    Requête permettant de lister les hashtags
    """

    join_post_post_type = get_jpp_type(inclure_citations, inclure_retweets, inclure_comments)


    _SQL = """
    WITH hashtags AS (
        SELECT 
            t.name as tag_name,
            v.post_id,
            v.account_id,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_engagements ELSE 0 END) AS post_engagements,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_reactions ELSE 0 END) AS post_reactions,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_comments ELSE 0 END) AS post_comments,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_shares ELSE 0 END) AS post_shares,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_views ELSE 0 END) AS post_views,
            MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_quotes ELSE 0 END) AS post_quotes,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN 1 ELSE 0 END) as citations,
            SUM(CASE WHEN v.join_post_post_type = 'share' THEN 1 ELSE 0 END) as repartages
        FROM v_posts_and_quotes_forwards_wt_texts_and_authors v
        LEFT JOIN join_post_tag jpt ON jpt.post_id = v.post_id
        LEFT JOIN tags t ON t.id = jpt.tag_id
        WHERE
            v.post_importation_id IN ({importation_id})
            and t.name is not null
            and v.join_post_post_type IN ({filter_jpp_type})
            {filter_by_date}
        GROUP BY t.name, v.post_id, v.account_id
        )
        SELECT 
            h.tag_name as hashtag,
            SUM(h.citations) as citations,
            SUM(h.repartages) as repartages,
            COUNT(DISTINCT h.post_id) AS verbatims,
            COUNT(DISTINCT h.account_id) AS users,
            SUM(h.post_engagements) AS engagements,
            SUM(h.post_views) AS views,
            SUM(h.post_reactions) AS reactions,
            SUM(h.post_shares) AS shares,
            SUM(h.post_comments) AS comments,
            SUM(h.post_quotes) AS quotes
        FROM hashtags h
        GROUP BY h.tag_name
        ORDER BY verbatims DESC;
     """

    _SQL = _SQL.format(
        importation_id=lst_of_int(importation_id),
        filter_jpp_type = lst_to_str(join_post_post_type),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date)
    )
    return text(_SQL)

def related_posts_to_domains(importation_id, start_date, end_date, inclure_citations, inclure_retweets, inclure_comments, domains):
    """
    Requête permettant de lister les posts associés à un ou plusieurs noms de domaines
    """

    join_post_post_type = get_jpp_type(inclure_citations, inclure_retweets, inclure_comments)


    _SQL = """
            SELECT 
                v.post_id,
                v.post_pf_post_id as pf_post_id,
                v.post_created_at as post_date, 
                v.account_id,
                v.pf_account_id,
                v.document_id,
                v.document_text,
                v.document_domain,
                v.document_url,
                v.post_url,      
                MAX(v.account_screen_name) as screen_name, 
                MAX(v.account_description) as description, 
                MAX(v.account_followers) as followers, 
                MAX(v.account_following) as followings, 
                MAX(v.account_posts) as user_posts, 
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_engagements ELSE 0 END) AS post_engagements,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_reactions ELSE 0 END) AS post_reactions,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_comments ELSE 0 END) AS post_comments,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_shares ELSE 0 END) AS post_shares,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_views ELSE 0 END) AS post_views,
                MAX(CASE WHEN v.join_post_post_type IN ('original', 'quote', 'comment') THEN v.post_quotes ELSE 0 END) AS post_quotes,
                SUM(CASE WHEN v.join_post_post_type = 'quote' THEN 1 ELSE 0 END) as citations,
                SUM(CASE WHEN v.join_post_post_type = 'share' THEN 1 ELSE 0 END) as repartages
            FROM v_posts_and_quotes_forwards_wt_texts_urls_and_authors v
            WHERE
                v.post_importation_id IN ({importation_id})
                and v.join_post_post_type IN ({filter_jpp_type})
                and v.document_domain IN ({filter_by_domain})
                {filter_by_date}
            GROUP BY 
                v.post_id,
                v.post_pf_post_id,
                v.post_created_at, 
                v.account_id,
                v.pf_account_id,
                v.document_id,
                v.document_text,
                v.document_domain,
                v.document_url,
                v.post_url
     """

    _SQL = _SQL.format(
        importation_id=lst_of_int(importation_id),
        filter_jpp_type = lst_to_str(join_post_post_type),
        filter_by_domain = lst_to_str(domains),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date)
    )
    return text(_SQL)

def q_accounts(importation_id, start_date, end_date, registered_start_date, registered_end_date, inclure_citations, inclure_retweets, inclure_comments):
    """
    Requête permettant de récupérer la liste des auteurs
    """

    # On prépare les filtres de sélection de posts / commentaires / retweets / citations
    jpp_type = get_jpp_type(inclure_citations, inclure_retweets, inclure_comments)

    _SQL = """
    WITH all_posts as (
        SELECT 
            post_importation_id,
            post_id, 
            account_id,
            pf_account_id,
            account_screen_name,
            account_name,
            account_registered_at,
            account_url,
            MAX(account_description) as description,
            MAX(account_followers) as followers,
            MAX(account_following) as followings,
            MAX(account_posts) as user_posts,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_engagements ELSE 0 END) AS post_engagements,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_reactions ELSE 0 END) AS post_reactions,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_comments ELSE 0 END) AS post_comments,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_shares ELSE 0 END) AS post_shares,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_views ELSE 0 END) AS post_views,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_quotes ELSE 0 END) AS post_quotes,
            SUM(CASE WHEN join_post_post_type = 'quote' THEN 1 ELSE 0 END) AS citations,
            SUM(CASE WHEN join_post_post_type = 'share' THEN 1 ELSE 0 END) AS repartages
        FROM v_posts_and_quotes_forwards_wt_texts_and_authors v
        WHERE 
            v.post_importation_id IN ({importations})
            and v.join_post_post_type IN ({filter_jpp_type})
            {filter_by_date}
            {filter_by_registered_at}
        GROUP BY post_id, account_id, pf_account_id, post_importation_id, account_name, account_screen_name, account_url, account_registered_at
    )
        SELECT 
            dp.pf_account_id,
            dp.account_screen_name,
            dp.account_name,
            dp.account_url,
            dp.description,
            MAX(followers) as followers,
            MAX(followings) as followings,
            MAX(user_posts) as user_posts,
            SUM(citations) as citations,
            SUM(repartages) as repartages,
            COUNT(DISTINCT dp.post_id) AS posts,
            SUM(dp.post_engagements) AS engagements,
            SUM(dp.post_views) AS views,
            SUM(dp.post_reactions) AS reactions,
            SUM(dp.post_shares) AS shares,
            SUM(dp.post_comments) AS comments,
            SUM(dp.post_quotes) AS quotes
        FROM all_posts dp
        GROUP BY dp.pf_account_id, dp.account_screen_name, dp.account_name, dp.account_url, dp.description
        ORDER BY Posts DESC;
"""

    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_jpp_type = lst_to_str(jpp_type),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date),
        filter_by_registered_at = filter_by_date("v.account_registered_at", registered_start_date, registered_end_date)
    )
    return text(_SQL)


def q_mentions(importation_id, start_date, end_date, registered_start_date, registered_end_date, inclure_citations, inclure_retweets, inclure_comments):
    """
    Requête permettant de récupérer la liste des utilisateurs mentionnés
    """

    # On prépare les filtres de sélection de posts / commentaires / retweets / citations
    jpp_type = get_jpp_type(inclure_citations, inclure_retweets, inclure_comments)

    _SQL = """
    WITH all_posts as (
        SELECT 
            post_importation_id,
            post_id, 
            mention_id,
            mention_pf_account_id,
            mention_screen_name,
            mention_name,
            mention_registered_at,
            mention_url,
            MAX(mention_description) as description,
            MAX(mention_followers) as followers,
            MAX(mention_following) as followings,
            MAX(mention_posts) as user_posts,
            count(distinct(author_id)) as accounts,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_engagements ELSE 0 END) AS post_engagements,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_reactions ELSE 0 END) AS post_reactions,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_comments ELSE 0 END) AS post_comments,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_shares ELSE 0 END) AS post_shares,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_views ELSE 0 END) AS post_views,
            MAX(CASE WHEN join_post_post_type IN ('original', 'quote', 'comment') THEN post_quotes ELSE 0 END) AS post_quotes,
            SUM(CASE WHEN join_post_post_type = 'quote' THEN 1 ELSE 0 END) AS citations,
            SUM(CASE WHEN join_post_post_type = 'share' THEN 1 ELSE 0 END) AS repartages
        FROM v_post_with_mentions v
        WHERE 
            v.post_importation_id IN ({importations})
            and v.join_post_post_type IN ({filter_jpp_type})
            {filter_by_date}
            {filter_by_registered_at}
        GROUP BY post_id, mention_id, mention_pf_account_id, post_importation_id, mention_name, mention_screen_name, mention_url, mention_registered_at
    )
        SELECT 
            dp.mention_id,
            dp.mention_pf_account_id,
            dp.mention_screen_name,
            dp.mention_name,
            dp.mention_registered_at,
            dp.mention_url,
            dp.description,
            MAX(dp.followers) as followers,
            MAX(dp.followings) as followings,
            MAX(dp.user_posts) as user_posts,
            SUM(accounts) as accounts,
            SUM(citations) as citations,
            SUM(repartages) as repartages,
            COUNT(DISTINCT dp.post_id) AS posts,
            SUM(dp.post_engagements) AS engagements,
            SUM(dp.post_views) AS views,
            SUM(dp.post_reactions) AS reactions,
            SUM(dp.post_shares) AS shares,
            SUM(dp.post_comments) AS comments,
            SUM(dp.post_quotes) AS quotes
        FROM all_posts dp
        GROUP BY 
            dp.mention_id,
            dp.mention_pf_account_id,
            dp.mention_screen_name,
            dp.mention_name,
            dp.mention_registered_at,
            dp.mention_url,
            dp.description
        ORDER BY Posts DESC;
"""

    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_jpp_type = lst_to_str(jpp_type),
        filter_by_date = filter_by_date("v.source_date", start_date, end_date),
        filter_by_registered_at = filter_by_date("v.mention_registered_at", registered_start_date, registered_end_date)
    )
    return text(_SQL)


def q_quoted_accounts(importation_id, reprise_start_date, reprise_end_date, citation_start_date, citation_end_date):
    """
    Liste des comptes les plus cités
    """

    _SQL = """
        SELECT 
            v.post_importation_id,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name AS screen_name,
            v.account_lang,
            v.account_url,
            MAX(v.account_description) AS description,
            MAX(v.account_registered_at) AS account_registered_at,
            MAX(v.account_profile_picture) AS account_profile_picture,
            MAX(v.account_followers) AS account_followers,
            MAX(v.account_following) AS account_following,
            MAX(v.account_posts) AS account_posts,
            MAX(v.account_views) AS account_views,
            count(DISTINCT v.post_id) AS posts,
            MAX(v.post_engagements) AS engagements,
            MAX(v.post_reactions) AS reactions,
            MAX(v.post_comments) AS comments,
            MAX(v.post_shares) AS shares,
            MAX(v.post_views) AS views,
            MAX(v.post_quotes) AS quotes,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN 1 ELSE 0 END) as citations,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_engagements ELSE 0 END) as engagement_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_reactions ELSE 0 END) as reactions_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_comments ELSE 0 END) as commentaires_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_shares ELSE 0 END) as partages_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_quotes ELSE 0 END) as quotes_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_views ELSE 0 END) as views_des_reprises
        FROM v_posts_and_quotes_forwards_wt_texts_and_authors v
        WHERE 
            v.post_importation_id IN ({importations})
            and v.join_post_post_type ='quote'
            {filter_by_date_1}
            {filter_by_date_2}
        GROUP BY 
            v.post_importation_id,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name,
            v.account_lang,
            v.account_url
        ORDER BY citations DESC
            ;"""
    
    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_by_date_1 = filter_by_date("v.source_date", reprise_start_date , reprise_end_date),
        filter_by_date_2 = filter_by_date("v.post_created_at", citation_start_date, citation_end_date)
    )
    return text(_SQL)

def q_shared_accounts(importation_id, reprise_start_date, reprise_end_date, citation_start_date, citation_end_date):
    """
    Liste des comptes les plus repartagés
    """

    _SQL = """
        SELECT 
            v.post_importation_id,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name AS screen_name,
            v.account_lang,
            v.account_url,
            MAX(v.account_description) AS description,
            MAX(v.account_registered_at) AS account_registered_at,
            MAX(v.account_profile_picture) AS account_profile_picture,
            MAX(v.account_followers) AS account_followers,
            MAX(v.account_following) AS account_following,
            MAX(v.account_posts) AS account_posts,
            MAX(v.account_views) AS account_views,
            count(DISTINCT v.post_id) AS posts,
            MAX(v.post_engagements) AS engagements,
            MAX(v.post_reactions) AS reactions,
            MAX(v.post_comments) AS comments,
            MAX(v.post_shares) AS shares,
            MAX(v.post_views) AS views,
            MAX(v.post_quotes) AS quotes,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN 1 ELSE 0 END) as citations,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_engagements ELSE 0 END) as engagement_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_reactions ELSE 0 END) as reactions_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_comments ELSE 0 END) as commentaires_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_shares ELSE 0 END) as partages_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_quotes ELSE 0 END) as quotes_des_reprises,
            SUM(CASE WHEN v.join_post_post_type = 'quote' THEN v.source_post_views ELSE 0 END) as views_des_reprises
        FROM v_posts_and_quotes_forwards_wt_texts_and_authors v
        WHERE 
            v.post_importation_id IN ({importations})
            and v.join_post_post_type ='share'
            {filter_by_date_1}
            {filter_by_date_2}
        GROUP BY 
            v.post_importation_id,
            v.account_id,
            v.pf_account_id,
            v.account_name,
            v.account_screen_name,
            v.account_lang,
            v.account_url
        ORDER BY citations DESC
            ;"""
    
    _SQL = _SQL.format(
        importations = lst_of_int(importation_id),
        filter_by_date_1 = filter_by_date("v.source_date", reprise_start_date , reprise_end_date),
        filter_by_date_2 = filter_by_date("v.post_created_at", citation_start_date, citation_end_date)
    )
    return text(_SQL)
