from ldap3 import Server, Connection, ALL, HASHED_SALTED_SHA
from ldap_config import LDAP_SERVER, BIND_DN, BIND_PASSWORD, BASE_DN

server = Server(LDAP_SERVER, get_info=all)
conn = Connection(server, BIND_DN, BIND_PASSWORD, auto_bind=True)

def add_user_entry(scim_user):
    
    user_dn = f"uid={scim_user.id}," + BASE_DN
    user_attributes = {
        'objectClass': ['top', 'inetOrgPerson'],
        'uid': scim_user.userName,          
        'cn': scim_user.name.formatted,        
        'sn': scim_user.name.familyName,       
        'givenName': scim_user.name.givenName,
        'employeeNumber': scim_user.externalId
    }

    if conn.add(user_dn, attributes=user_attributes):
        print(f"User {user_dn} added successfully!")
    else:
        print(f"Failed to add user: {conn.result}")

def get_user_entry(search_uid):
    
    conn.search(
        search_base=BASE_DN,
        search_scope="SUBTREE",
        search_filter=f'(uid = {search_uid})',
        attributes=['*']
    )

    if conn.entries:
        user_entry = conn.entries[0]
        print(f"Found user: {user_entry.entry_dn}")
        print(user_entry.entry_attributes_as_dict)
    else:
        print(f"No user found with uid={search_uid}")


def delete_user_entry(search_uid):
    
    if conn.delete(f"uid={search_uid},{BASE_DN}"):
        print(f"User {search_uid} deleted successfully!")
    else:
        print(f"Failed to delete user: {conn.result}")
