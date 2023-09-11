#!groovy
import hudson.security.*
import jenkins.model.*
import org.jenkinsci.plugins.matrixauth.PermissionEntry
import org.jenkinsci.plugins.matrixauth.AuthorizationType

def instance = Jenkins.getInstance()
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
def users = hudsonRealm.getAllUsers()
usersCollect = users.collect { it.toString() }

// Create the admin user account if it doesn't already exist.
if ("admin" in usersCollect) {
    println "Admin user already exists - updating password"

    def user = hudson.model.User.get('admin');
    def password = hudson.security.HudsonPrivateSecurityRealm.Details.fromPlainPassword('admin')
    user.addProperty(password)
    user.save()
}
else {
    println "--> Creating local admin user"

    hudsonRealm.createAccount('admin', '1235678')
    instance.setSecurityRealm(hudsonRealm)

    def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
    instance.setAuthorizationStrategy(strategy)

    // 创建授权入口为user
    def permission_entry = new PermissionEntry(AuthorizationType.USER, "admin")
    // 新增ADMINISTER策略
    instance.authorizationStrategy.add(Jenkins.ADMINISTER, permission_entry)
    instance.save()
    println "--> Creating admin roles user successed"
}
