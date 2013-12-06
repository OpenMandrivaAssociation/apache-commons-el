%global base_name       el
%global short_name      commons-%{base_name}


Name:           apache-%{short_name}
Version:        1.0
Release:        26
Summary:        The Apache Commons Extension Language
License:        ASL 1.1
Group:          Development/Java
URL:            http://commons.apache.org/%{base_name}
BuildArch:      noarch
Source0:        http://archive.apache.org/dist/commons/%{base_name}/source/%{short_name}-%{version}-src.tar.gz
Source1:        %{short_name}-%{version}.pom
Patch0:         %{short_name}-%{version}-license.patch
Patch1:         %{short_name}-eclipse-manifest.patch
Patch2:         %{short_name}-enum.patch
Requires(post): jpackage-utils
Requires(postun): jpackage-utils
BuildRequires:  jpackage-utils >= 0:1.6
BuildRequires:  ant
BuildRequires:  tomcat-jsp-2.2-api
BuildRequires:  tomcat-servlet-3.0-api
BuildRequires:  junit
BuildRequires:  java-1.6.0-openjdk-devel

# This should go away with F-17
Provides:       jakarta-%{short_name} = 0:%{version}-%{release}
Obsoletes:      jakarta-%{short_name} < 0:%{version}-%{release}

%description
An implementation of standard interfaces and abstract classes for
javax.servlet.jsp.el which is part of the JSP 2.0 specification.

%package        javadoc
Summary:        API documentation for %{name}
Group:          Development/Java
Requires:       jpackage-utils

Provides:       jakarta-%{short_name}-javadoc = 0:%{version}-%{release}
Obsoletes:      jakarta-%{short_name}-javadoc < 0:%{version}-%{release}


%description    javadoc
%{summary}.


%prep
%setup -q -n %{short_name}-%{version}-src
%patch0 -p1 -b .license
%patch1 -p1
%patch2 -p1

# remove all precompiled stuff
find . -type f -name "*.jar" -exec rm -f {} \;

cat > build.properties <<EOBP
build.compiler=modern
junit.jar=$(build-classpath junit)
servlet-api.jar=$(build-classpath tomcat-servlet-3.0-api)
jsp-api.jar=$(build-classpath tomcat-jsp-2.2-api)
servletapi.build.notrequired=true
jspapi.build.notrequired=true
EOBP

%build
export CLASSPATH=
export OPT_JAR_LIST=:
ant \
  -Dfinal.name=%{short_name} \
  -Dj2se.javadoc=%{_javadocdir}/java \
  jar javadoc


%install
rm -rf $RPM_BUILD_ROOT

# jars
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -p -m 644 dist/%{short_name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
pushd $RPM_BUILD_ROOT%{_javadir}
for jar in *-%{version}*; do
    ln -sf ${jar} `echo $jar| sed "s|apache-||g"`
    ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`
    ln -sf ${jar} `echo $jar| sed "s|apache-\(.*\)-%{version}|\1|g"`
done
popd # come back from javadir

# pom
install -pD -T -m 644 %{SOURCE1} %{buildroot}%{_mavenpomdir}/JPP-%{short_name}.pom
%add_to_maven_depmap org.apache.commons %{short_name} %{version} JPP %{short_name}

# following line is only for backwards compatibility. New packages
# should use proper groupid org.apache.commons
%add_to_maven_depmap commons-el commons-el %{version} JPP %{short_name}

# javadoc
install -d -m 755 $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr dist/docs/api/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}



%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%defattr(-,root,root,-)
%doc LICENSE.txt STATUS.html
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{name}.jar
%{_javadir}/%{short_name}-%{version}.jar
%{_javadir}/%{short_name}.jar
%{_mavenpomdir}/JPP-%{short_name}.pom
%{_mavendepmapfragdir}/%{name}

%files javadoc
%defattr(-,root,root,-)
%doc LICENSE.txt
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}


