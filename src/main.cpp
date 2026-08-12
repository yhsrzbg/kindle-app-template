#include <gtk-2.0/gtk/gtk.h>

#include <string>

#include "app_config.hpp"

namespace {

void on_exit_clicked(GtkWidget*, gpointer window) {
  gtk_widget_destroy(GTK_WIDGET(window));
}

}  // namespace

int main(int argc, char* argv[]) {
  gtk_init(&argc, &argv);

  GtkWidget* window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
  const std::string title =
      std::string("L:A_N:application_ID:") + APP_WINDOW_ID + "_PC:T";
  gtk_window_set_title(GTK_WINDOW(window), title.c_str());
  gtk_window_set_default_size(GTK_WINDOW(window), 600, 800);
  gtk_window_maximize(GTK_WINDOW(window));
  gtk_container_set_border_width(GTK_CONTAINER(window), 36);

  GtkWidget* layout = gtk_vbox_new(FALSE, 24);
  GtkWidget* heading = gtk_label_new(nullptr);
  const std::string markup =
      std::string("<span size=\"xx-large\" weight=\"bold\">") + APP_NAME +
      "</span>\n\n<span size=\"large\">Hello, Kindle World!</span>";
  gtk_label_set_markup(GTK_LABEL(heading), markup.c_str());
  gtk_label_set_justify(GTK_LABEL(heading), GTK_JUSTIFY_CENTER);

  GtkWidget* version = gtk_label_new((std::string("Version ") + APP_VERSION).c_str());
  GtkWidget* exit_button = gtk_button_new_with_label("Exit");
  gtk_widget_set_size_request(exit_button, 240, 72);

  gtk_box_pack_start(GTK_BOX(layout), heading, TRUE, TRUE, 0);
  gtk_box_pack_start(GTK_BOX(layout), version, FALSE, FALSE, 0);
  gtk_box_pack_start(GTK_BOX(layout), exit_button, FALSE, FALSE, 0);
  gtk_container_add(GTK_CONTAINER(window), layout);

  g_signal_connect(exit_button, "clicked", G_CALLBACK(on_exit_clicked), window);
  g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), nullptr);

  gtk_widget_show_all(window);
  gtk_main();
  return 0;
}
