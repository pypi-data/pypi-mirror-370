#!/usr/bin/env bash

set -e

# Use environment variables with defaults
SSL_FOLDER=${SSL_FOLDER:-$(pwd)}
HOSTNAME=${RABBITMQ_HOSTNAME:-localhost}
COUNTRY=${SSL_COUNTRY:-ES}
STATE=${SSL_STATE:-Catalonia}
CITY=${SSL_CITY:-Barcelona}
ORG=${SSL_ORG:-ERNI}
OU=${SSL_OU:-Development}
DAYS=${SSL_CERT_DAYS:-3650}

# Certificate file paths
CA_KEY=${SSL_FOLDER}/ca_key.pem
CA_CERTIFICATE=${SSL_FOLDER}/ca_certificate.pem
SERVER_KEY=${SSL_FOLDER}/server_key.pem
SERVER_CERTIFICATE=${SSL_FOLDER}/server_certificate.pem
CLIENT_KEY=${SSL_FOLDER}/client_key.pem
CLIENT_CERTIFICATE=${SSL_FOLDER}/client_certificate.pem

echo "Generating SSL certificates in ${SSL_FOLDER}..."

# Generate CA private key
echo "Generating CA private key..."
openssl genrsa -out ${CA_KEY} 4096

# Generate CA certificate
echo "Generating CA certificate..."
openssl req -new -x509 -days ${DAYS} -key ${CA_KEY} -out ${CA_CERTIFICATE} \
    -subj "/C=${COUNTRY}/ST=${STATE}/L=${CITY}/O=${ORG}/OU=${OU}/CN=${HOSTNAME}-ca"

# Generate server private key
echo "Generating server private key..."
openssl genrsa -out ${SERVER_KEY} 4096

# Generate server certificate signing request
echo "Generating server certificate signing request..."
openssl req -new -key ${SERVER_KEY} -out server.csr \
    -subj "/C=${COUNTRY}/ST=${STATE}/L=${CITY}/O=${ORG}/OU=${OU}/CN=${HOSTNAME}"

# Generate server certificate signed by CA
echo "Generating server certificate..."
openssl x509 -req -in server.csr -CA ${CA_CERTIFICATE} -CAkey ${CA_KEY} \
    -CAcreateserial -out ${SERVER_CERTIFICATE} -days ${DAYS} \
    -extensions v3_req -extfile <(cat <<EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${HOSTNAME}
DNS.2 = localhost
IP.1 = 127.0.0.1
EOF
)

# Generate client private key (optional, for client certificate authentication)
echo "Generating client private key..."
openssl genrsa -out ${CLIENT_KEY} 4096

# Generate client certificate signing request
echo "Generating client certificate signing request..."
openssl req -new -key ${CLIENT_KEY} -out client.csr \
    -subj "/C=${COUNTRY}/ST=${STATE}/L=${CITY}/O=${ORG}/OU=${OU}/CN=${HOSTNAME}-client"

# Generate client certificate signed by CA
echo "Generating client certificate..."
openssl x509 -req -in client.csr -CA ${CA_CERTIFICATE} -CAkey ${CA_KEY} \
    -CAcreateserial -out ${CLIENT_CERTIFICATE} -days ${DAYS} \
    -extensions v3_req -extfile <(cat <<EOF
[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = clientAuth
EOF
)

# Clean up CSR files
rm -f server.csr client.csr

# Set appropriate permissions - make keys readable by rabbitmq user
chmod 644 ${CA_KEY} ${SERVER_KEY} ${CLIENT_KEY}
chmod 644 ${CA_CERTIFICATE} ${SERVER_CERTIFICATE} ${CLIENT_CERTIFICATE}

echo "SSL certificates generated successfully!"
echo "Files created in ${SSL_FOLDER}:"
echo "  - ca_certificate.pem (CA certificate)"
echo "  - ca_key.pem (CA private key)"
echo "  - server_certificate.pem (Server certificate)"
echo "  - server_key.pem (Server private key)"
echo "  - client_certificate.pem (Client certificate)"
echo "  - client_key.pem (Client private key)"