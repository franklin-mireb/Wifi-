<?php
/**
 * Plugin Name: WiFi Manager Integration
 * Description: Intègre le système WiFi Manager avec vouchers dans WordPress
 * Version: 1.0.0
 * Author: franklin-mireb
 */

// Sécurité WordPress
if (!defined('ABSPATH')) {
    exit;
}

class WiFiManagerWordPress {
    
    private $wifi_api_url = 'http://localhost:5000/api';
    
    public function __construct() {
        add_action('init', array($this, 'init'));
        add_action('wp_enqueue_scripts', array($this, 'enqueue_scripts'));
        add_shortcode('wifi_manager', array($this, 'wifi_manager_shortcode'));
        add_shortcode('wifi_vouchers', array($this, 'wifi_vouchers_shortcode'));
        
        // API REST WordPress
        add_action('rest_api_init', array($this, 'register_api_routes'));
    }
    
    public function init() {
        // Initialisation
    }
    
    public function enqueue_scripts() {
        wp_enqueue_script('jquery');
        wp_enqueue_script('bootstrap', 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js');
        wp_enqueue_style('bootstrap', 'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css');
        wp_enqueue_style('fontawesome', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');
    }
    
    /**
     * Shortcode pour l'interface WiFi Manager
     */
    public function wifi_manager_shortcode($atts) {
        $atts = shortcode_atts(array(
            'type' => 'full',
            'height' => '600px'
        ), $atts);
        
        ob_start();
        ?>
        <div class="wifi-manager-container" style="height: <?php echo esc_attr($atts['height']); ?>;">
            <iframe 
                src="http://localhost:5000" 
                width="100%" 
                height="100%" 
                frameborder="0"
                style="border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            </iframe>
        </div>
        <?php
        return ob_get_clean();
    }
    
    /**
     * Shortcode pour le système de vouchers
     */
    public function wifi_vouchers_shortcode($atts) {
        $atts = shortcode_atts(array(
            'plan' => 'both',
            'style' => 'cards'
        ), $atts);
        
        ob_start();
        ?>
        <div class="wifi-vouchers-widget">
            <div class="container">
                <div class="row">
                    <?php if ($atts['plan'] == 'both' || $atts['plan'] == 'daily'): ?>
                    <div class="col-md-6 mb-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5 class="card-title">
                                    <i class="fas fa-clock text-primary"></i>
                                    Accès 1 Jour
                                </h5>
                                <p class="card-text">
                                    <span class="h3 text-success">0,60$</span>
                                    <small class="text-muted">/jour</small>
                                </p>
                                <button class="btn btn-primary btn-voucher" data-plan="daily" data-amount="0.6">
                                    Acheter maintenant
                                </button>
                            </div>
                        </div>
                    </div>
                    <?php endif; ?>
                    
                    <?php if ($atts['plan'] == 'both' || $atts['plan'] == 'monthly'): ?>
                    <div class="col-md-6 mb-4">
                        <div class="card">
                            <div class="card-body text-center">
                                <h5 class="card-title">
                                    <i class="fas fa-calendar text-success"></i>
                                    Accès 1 Mois
                                </h5>
                                <p class="card-text">
                                    <span class="h3 text-success">7,00$</span>
                                    <small class="text-muted">/mois</small>
                                    <br><small class="badge bg-warning">Économisez 40%</small>
                                </p>
                                <button class="btn btn-success btn-voucher" data-plan="monthly" data-amount="7">
                                    Acheter maintenant
                                </button>
                            </div>
                        </div>
                    </div>
                    <?php endif; ?>
                </div>
                
                <!-- Zone de résultat -->
                <div id="voucher-result" class="mt-4" style="display: none;">
                    <div class="alert alert-success">
                        <h5><i class="fas fa-ticket-alt"></i> Votre Code WiFi</h5>
                        <p class="mb-2">Votre code d'accès :</p>
                        <div class="input-group">
                            <input type="text" class="form-control" id="voucher-code" readonly>
                            <button class="btn btn-outline-secondary" onclick="copyVoucherCode()">
                                <i class="fas fa-copy"></i> Copier
                            </button>
                        </div>
                        <small class="text-muted">Utilisez ce code pour vous connecter au WiFi</small>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        jQuery(document).ready(function($) {
            $('.btn-voucher').click(function() {
                var plan = $(this).data('plan');
                var amount = $(this).data('amount');
                
                // Simulation achat (remplacer par vraie API)
                $.ajax({
                    url: '<?php echo $this->wifi_api_url; ?>/voucher/purchase',
                    method: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        plan: plan,
                        amount: amount
                    }),
                    success: function(response) {
                        if (response.success) {
                            $('#voucher-code').val(response.voucher_code);
                            $('#voucher-result').show();
                        } else {
                            alert('Erreur lors de l\'achat: ' + response.message);
                        }
                    },
                    error: function() {
                        alert('Erreur de connexion au serveur WiFi');
                    }
                });
            });
        });
        
        function copyVoucherCode() {
            var code = document.getElementById('voucher-code');
            code.select();
            document.execCommand('copy');
            alert('Code copié dans le presse-papier !');
        }
        </script>
        <?php
        return ob_get_clean();
    }
    
    /**
     * API REST pour WordPress
     */
    public function register_api_routes() {
        register_rest_route('wifi-manager/v1', '/voucher/purchase', array(
            'methods' => 'POST',
            'callback' => array($this, 'api_purchase_voucher'),
            'permission_callback' => '__return_true'
        ));
        
        register_rest_route('wifi-manager/v1', '/voucher/validate', array(
            'methods' => 'POST', 
            'callback' => array($this, 'api_validate_voucher'),
            'permission_callback' => '__return_true'
        ));
    }
    
    public function api_purchase_voucher($request) {
        $params = $request->get_json_params();
        
        // Proxy vers l'API WiFi Manager
        $response = wp_remote_post($this->wifi_api_url . '/voucher/purchase', array(
            'headers' => array('Content-Type' => 'application/json'),
            'body' => wp_json_encode($params)
        ));
        
        if (is_wp_error($response)) {
            return new WP_Error('api_error', 'Erreur de connexion', array('status' => 500));
        }
        
        return json_decode(wp_remote_retrieve_body($response), true);
    }
    
    public function api_validate_voucher($request) {
        $params = $request->get_json_params();
        
        // Proxy vers l'API WiFi Manager
        $response = wp_remote_post($this->wifi_api_url . '/voucher/validate', array(
            'headers' => array('Content-Type' => 'application/json'),
            'body' => wp_json_encode($params)
        ));
        
        if (is_wp_error($response)) {
            return new WP_Error('api_error', 'Erreur de connexion', array('status' => 500));
        }
        
        return json_decode(wp_remote_retrieve_body($response), true);
    }
}

// Initialiser le plugin
new WiFiManagerWordPress();

/**
 * Fonction pour activer le plugin
 */
function wifi_manager_activate() {
    // Code d'activation
}
register_activation_hook(__FILE__, 'wifi_manager_activate');

/**
 * Fonction pour désactiver le plugin
 */
function wifi_manager_deactivate() {
    // Code de désactivation
}
register_deactivation_hook(__FILE__, 'wifi_manager_deactivate');
?>
