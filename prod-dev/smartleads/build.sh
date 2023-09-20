python -m nuitka \
--standalone \
--output-dir=build \
--include-package-data=feature_engine \
--include-package-data=SmartLeads \
--include-package-data=streamlit \
--include-package-data=streamlit_option_menu \
--include-package=kedro \
--include-package=openpyxl \
--include-package=plotly \
--include-package=SmartLeads \
--include-package=streamlit \
--include-data-file=src/SmartLeads/streamlit_app/app.py=SmartLeads/streamlit_app/app.py \
--include-module=_scproxy \
--macos-create-app-bundle \
--user-package-configuration-file=user-package-configuration.yml \
--noinclude-IPython-mode=nofollow \
--report=report.xml \
src/SmartLeads/SmartLeads-tool.py