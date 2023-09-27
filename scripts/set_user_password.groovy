#!groovy
import hudson.security.*
import jenkins.model.*
import org.jenkinsci.plugins.matrixauth.PermissionEntry
import org.jenkinsci.plugins.matrixauth.AuthorizationType

def env = System.getenv()
def jenkins = Jenkins.getInstance()
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
def users = hudsonRealm.getAllUsers()
usersCollect = users.collect { it.toString() }

// Create the admin user account if it doesn't already exist.
if ("admin" in usersCollect) {
    println "Admin user already exists - updating password"

    def user = hudson.model.User.get('admin');
    def password = hudson.security.HudsonPrivateSecurityRealm.Details.fromPlainPassword('1235678')
    user.addProperty(password)
    user.save()
}
else {
	println "--> Creating local admin user"
    if(!(jenkins.getSecurityRealm() instanceof HudsonPrivateSecurityRealm))
		jenkins.setSecurityRealm(new HudsonPrivateSecurityRealm(false))
	if(!(jenkins.getAuthorizationStrategy() instanceof GlobalMatrixAuthorizationStrategy))
		jenkins.setAuthorizationStrategy(new GlobalMatrixAuthorizationStrategy())
	def user = jenkins.getSecurityRealm().createAccount(env.JENKINS_USER, env.JENKINS_PASSWORD)
	user.save()
	println "-->Add AuthorizationStrategy"
	jenkins.getAuthorizationStrategy().add(Jenkins.ADMINISTER, env.JENKINS_USER)
	jenkins.save()
	println "--> Creating admin roles user successed"
}
