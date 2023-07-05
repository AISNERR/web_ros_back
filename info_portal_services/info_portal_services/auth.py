from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth.models import Group


class UserFromKeycloak(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super(UserFromKeycloak, self).create_user(claims)
        self.map_user_data(user, claims)
        return user

    def filter_users_by_claims(self, claims):
        email = claims.get('email')
        preferred_username = claims.get('preferred_username')

        if not email:
            return self.UserModel.objects.none()
        users = self.UserModel.objects.filter(email__iexact=email)

        if len(users) < 1:
            if not preferred_username:
                return self.UserModel.objects.none()
            users = self.UserModel.objects.filter(username__iexact=preferred_username)
        return users

    def update_user(self, user, claims):
        self.map_user_data(user, claims)
        return user
    
    def map_user_data(self, user, claims):
        user.first_name = claims.get('given_name', '')
        user.last_name = claims.get('family_name', '')
        user.email = claims.get('email')
        user.username = claims.get('preferred_username')
        usergroups = claims.get('groups', [])
        for group_name in usergroups:
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
        user.save()
