1. Login: role{admin, user/farmer, expert}

2. Decription of how to make role and permission
- You need to write code manage of role and permission in route file
  Example in project: 
  @login_required
  @role_required("Admin")
  @permission_required("PERMISSION_AUDIT")