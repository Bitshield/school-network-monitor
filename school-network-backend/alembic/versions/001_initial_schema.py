"""Create initial schema

Revision ID: 001
Revises: 
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables."""
    
    # Create devices table
    op.create_table(
        'devices',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('device_type', sa.String(), nullable=False),
        sa.Column('ip', sa.String(length=45), nullable=True),
        sa.Column('mac', sa.String(length=17), nullable=True),
        sa.Column('hostname', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('last_seen', sa.DateTime(), nullable=False),
        sa.Column('is_monitored', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('vlan_id', sa.Integer(), nullable=True),
        sa.Column('subnet', sa.String(length=45), nullable=True),
        sa.Column('snmp_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('snmp_community', sa.String(length=255), nullable=True),
        sa.Column('snmp_version', sa.String(length=5), nullable=False, server_default='2c'),
        sa.Column('position_x', sa.Float(), nullable=True),
        sa.Column('position_y', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ip'),
        sa.UniqueConstraint('mac')
    )
    op.create_index('ix_devices_device_type', 'devices', ['device_type'])
    op.create_index('ix_devices_ip', 'devices', ['ip'])
    op.create_index('ix_devices_mac', 'devices', ['mac'])
    op.create_index('ix_devices_name', 'devices', ['name'])
    op.create_index('ix_devices_status', 'devices', ['status'])

    # Create ports table
    op.create_table(
        'ports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('device_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('port_number', sa.Integer(), nullable=False),
        sa.Column('port_name', sa.String(length=50), nullable=False),
        sa.Column('port_type', sa.String(), nullable=False, server_default='ETHERNET'),
        sa.Column('status', sa.String(), nullable=False, server_default='UNKNOWN'),
        sa.Column('is_up', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('speed_mbps', sa.Float(), nullable=True),
        sa.Column('max_speed_mbps', sa.Float(), nullable=True),
        sa.Column('mtu', sa.Integer(), nullable=True),
        sa.Column('duplex', sa.String(length=50), nullable=True),
        sa.Column('vlan_id', sa.Integer(), nullable=True),
        sa.Column('is_trunk', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('allowed_vlans', sa.String(length=255), nullable=True),
        sa.Column('native_vlan', sa.Integer(), nullable=True),
        sa.Column('mac_address', sa.String(length=17), nullable=True),
        sa.Column('rx_bytes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rx_packets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rx_errors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rx_dropped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tx_bytes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tx_packets', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tx_errors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('tx_dropped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('in_octets', sa.Float(), nullable=False, server_default='0'),
        sa.Column('in_discards', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('out_octets', sa.Float(), nullable=False, server_default='0'),
        sa.Column('out_errors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('out_discards', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('crc_errors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('frame_errors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('collision_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('connected_to', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_seen', sa.DateTime(), nullable=False),
        sa.Column('last_check', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_ports_device_id', 'ports', ['device_id'])
    op.create_index('ix_ports_status', 'ports', ['status'])

    # Create links table
    op.create_table(
        'links',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('source_device_id', sa.String(), nullable=False),
        sa.Column('target_device_id', sa.String(), nullable=False),
        sa.Column('source_port_id', sa.String(), nullable=True),
        sa.Column('target_port_id', sa.String(), nullable=True),
        sa.Column('link_type', sa.String(), nullable=False, server_default='PHYSICAL'),
        sa.Column('status', sa.String(), nullable=False, server_default='UNKNOWN'),
        sa.Column('bandwidth', sa.Integer(), nullable=True),
        sa.Column('speed_mbps', sa.Float(), nullable=True),
        sa.Column('duplex', sa.String(length=50), nullable=True),
        sa.Column('utilization', sa.Float(), nullable=False, server_default='0'),
        sa.Column('packet_loss', sa.Float(), nullable=False, server_default='0'),
        sa.Column('latency', sa.Float(), nullable=False, server_default='0'),
        sa.Column('jitter', sa.Float(), nullable=False, server_default='0'),
        sa.Column('cost', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_seen', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['source_device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_port_id'], ['ports.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['target_port_id'], ['ports.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_links_source_device_id', 'links', ['source_device_id'])
    op.create_index('ix_links_target_device_id', 'links', ['target_device_id'])
    op.create_index('ix_links_status', 'links', ['status'])

    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('device_id', sa.String(), nullable=True),
        sa.Column('port_id', sa.String(), nullable=True),
        sa.Column('link_id', sa.String(), nullable=True),
        sa.Column('message', sa.String(length=1000), nullable=False),
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('acknowledged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('acknowledged_by', sa.String(length=100), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('resolved_by', sa.String(length=100), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolution_notes', sa.String(length=1000), nullable=True),
        sa.Column('auto_resolved', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notification_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notification_sent_at', sa.DateTime(), nullable=True),
        sa.Column('occurrence_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('first_occurred_at', sa.DateTime(), nullable=False),
        sa.Column('last_occurred_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['port_id'], ['ports.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['link_id'], ['links.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_events_event_type', 'events', ['event_type'])
    op.create_index('ix_events_severity', 'events', ['severity'])
    op.create_index('ix_events_device_id', 'events', ['device_id'])
    op.create_index('ix_events_created_at', 'events', ['created_at'])
    op.create_index('ix_events_acknowledged', 'events', ['acknowledged'])
    op.create_index('ix_events_resolved', 'events', ['resolved'])
    op.create_index('ix_events_source', 'events', ['source'])
    op.create_index('idx_event_type_severity', 'events', ['event_type', 'severity'])
    op.create_index('idx_event_acknowledged', 'events', ['acknowledged', 'created_at'])
    op.create_index('idx_event_device_type', 'events', ['device_id', 'event_type'])
    op.create_index('idx_event_severity_created', 'events', ['severity', 'created_at'])

    # Create cable_health_metrics table
    op.create_table(
        'cable_health_metrics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('link_id', sa.String(), nullable=False),
        sa.Column('cable_type', sa.String(), nullable=False, server_default='UNKNOWN'),
        sa.Column('status', sa.String(), nullable=False, server_default='UNKNOWN'),
        sa.Column('length', sa.Float(), nullable=True),
        sa.Column('signal_strength', sa.Float(), nullable=True),
        sa.Column('signal_quality', sa.Integer(), nullable=True),
        sa.Column('noise_level', sa.Float(), nullable=True),
        sa.Column('snr', sa.Float(), nullable=True),
        sa.Column('attenuation', sa.Float(), nullable=True),
        sa.Column('impedance', sa.Float(), nullable=True),
        sa.Column('latency_ms', sa.Float(), nullable=True),
        sa.Column('packet_loss_percent', sa.Float(), nullable=False, server_default='0'),
        sa.Column('jitter_ms', sa.Float(), nullable=True),
        sa.Column('bit_error_rate', sa.Float(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('discard_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('crc_errors', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('pair1_status', sa.String(length=50), nullable=True),
        sa.Column('pair2_status', sa.String(length=50), nullable=True),
        sa.Column('pair3_status', sa.String(length=50), nullable=True),
        sa.Column('pair4_status', sa.String(length=50), nullable=True),
        sa.Column('health_score', sa.Float(), nullable=False, server_default='100'),
        sa.Column('test_date', sa.DateTime(), nullable=False),
        sa.Column('next_test_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('measured_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['link_id'], ['links.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cable_health_metrics_link_id', 'cable_health_metrics', ['link_id'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('ix_cable_health_metrics_link_id', table_name='cable_health_metrics')
    op.drop_table('cable_health_metrics')
    
    op.drop_index('idx_event_severity_created', table_name='events')
    op.drop_index('idx_event_device_type', table_name='events')
    op.drop_index('idx_event_acknowledged', table_name='events')
    op.drop_index('idx_event_type_severity', table_name='events')
    op.drop_index('ix_events_source', table_name='events')
    op.drop_index('ix_events_resolved', table_name='events')
    op.drop_index('ix_events_acknowledged', table_name='events')
    op.drop_index('ix_events_created_at', table_name='events')
    op.drop_index('ix_events_device_id', table_name='events')
    op.drop_index('ix_events_severity', table_name='events')
    op.drop_index('ix_events_event_type', table_name='events')
    op.drop_table('events')
    
    op.drop_index('ix_links_status', table_name='links')
    op.drop_index('ix_links_target_device_id', table_name='links')
    op.drop_index('ix_links_source_device_id', table_name='links')
    op.drop_table('links')
    
    op.drop_index('ix_ports_status', table_name='ports')
    op.drop_index('ix_ports_device_id', table_name='ports')
    op.drop_table('ports')
    
    op.drop_index('ix_devices_status', table_name='devices')
    op.drop_index('ix_devices_name', table_name='devices')
    op.drop_index('ix_devices_mac', table_name='devices')
    op.drop_index('ix_devices_ip', table_name='devices')
    op.drop_index('ix_devices_device_type', table_name='devices')
    op.drop_table('devices')