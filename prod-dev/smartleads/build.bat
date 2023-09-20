python -m nuitka ^
--standalone ^
--onefile ^
--output-dir=build ^
--include-package-data=feature_engine ^
--include-package-data=SmartLeads ^
--include-package-data=streamlit ^
--include-package-data=streamlit_option_menu ^
--include-package=kedro ^
--include-package=plotly ^
--include-package=SmartLeads ^
--include-package=streamlit ^
--include-data-file=src/SmartLeads/streamlit_app/app.py=SmartLeads/streamlit_app/app.py ^
--noinclude-IPython-mode=nofollow ^
--user-package-configuration-file=user-package-configuration.yml ^
--report=report.xml ^
--msvc=latest ^
--clang ^
src/SmartLeads/SmartLeads-tool.py