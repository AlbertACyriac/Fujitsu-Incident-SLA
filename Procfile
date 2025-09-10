cat > Procfile <<'EOF'
release: flask db upgrade
web: gunicorn wsgi:app
EOF
