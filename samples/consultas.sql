select 	c.catalog_id,
	c.name,
	r.repo_id,
	r.name,
	p.path || ifnull('\' + d.folder, '') || '\' || d.file as 'PathFinal',
	from catalog c
	inner join catalog_repos cr
		on cr.catalog_id = c.catalog_id
	inner join repo r
		on cr.repo_id = r.repo_id
	inner join repo_paths rp
		on  r.repo_id = rp.repo_id
	inner join path p
		on p.path_id = rp.path_id
	inner join path_databases pd
		on p.path_id = pd.path_id
	inner join database d
		on d.database_id = pd.database_id
		