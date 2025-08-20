version: "3.9"
name: ${stack_name}

services:
% for name, svc in services.items():
  ${name}:
    image: ${svc['image']}
% if 'build' in svc:
    build:
      context: ${svc['build'].get('context', '.')}
      dockerfile: ${svc['build'].get('dockerfile', 'Dockerfile')}
% endif
% if 'command' in svc:
    command: ${svc['command']}
% endif
% if 'environment' in svc:
    environment:
% for k, v in svc['environment'].items():
      ${k}: "${v}"
% endfor
% endif
% if 'ports' in svc:
    ports:
% for p in svc['ports']:
      - "${p}"
% endfor
% endif

% endfor

volumes:
% for v in volumes:
  ${v}: {}
% endfor

% if networks:
networks:
  cool:
    % if name:
    name: ${net_name}
    % endif
% endif
